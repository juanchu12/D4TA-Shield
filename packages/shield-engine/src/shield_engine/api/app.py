"""FastAPI application for D4TA Shield analysis engine."""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from shield_engine.analysis.pipeline import run_analysis
from shield_engine.api.schemas import (
    AnalysisSchema,
    AnalyzeResponse,
    ClauseDetailSchema,
    ClausePositionSchema,
    ClauseSchema,
    ReportSchema,
    UploadResponse,
)
from shield_engine.config import settings
from shield_engine.extraction.cascade import load_pdf
from shield_engine.extraction.docx_loader import load_docx
from shield_engine.models import ContractRecord, ContractStatus, new_id, utcnow
from shield_engine.segmentation.clause_parser import build_page_offsets, segment_clauses
from shield_engine.store.sqlite import store

logger = logging.getLogger(__name__)

REQUESTS = Counter("shield_engine_requests_total", "Requests", ["endpoint", "status"])
LATENCY = Histogram("shield_engine_request_latency_seconds", "Latency", ["endpoint"])

app = FastAPI(
    title="D4TA Shield Engine",
    version="0.1.0",
    description="Contract clause risk analysis — not legal advice.",
)


def require_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    if not x_internal_token or x_internal_token != settings.internal_token:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Internal-Token")


def _analysis_schema(a) -> AnalysisSchema:
    return AnalysisSchema(
        clause_id=a.clause_id,
        category=a.category.value,
        risk_level=a.risk_level.value,
        explanation=a.explanation,
        quoted_evidence=a.quoted_evidence,
        detected_by=a.detected_by.value,
        requires_priority_review=a.requires_priority_review,
        discrepancy_reason=a.discrepancy_reason,
    )


def _clause_schema(c) -> ClauseSchema:
    return ClauseSchema(
        id=c.id,
        index=c.index,
        title=c.title,
        text=c.text,
        position=ClausePositionSchema(
            page=c.position.page,
            char_start=c.position.char_start,
            char_end=c.position.char_end,
        ),
    )


@app.get("/health")
def health() -> dict[str, Any]:
    db_ok = settings.sqlite_path.exists() or True
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "shield-engine",
        "openai_configured": bool(settings.openai_api_key),
        "db_path": str(settings.sqlite_path),
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/contracts/upload", dependencies=[Depends(require_internal_token)])
async def upload_contract(file: UploadFile = File(...)) -> UploadResponse:
    start = time.perf_counter()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    contract_id = new_id()
    dest = settings.uploads_dir / f"{contract_id}{suffix}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    contract = ContractRecord(
        id=contract_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        status=ContractStatus.UPLOADED,
        file_path=str(dest),
    )

    try:
        if suffix == ".pdf":
            full_text, pages = load_pdf(dest)
            page_pairs = [(p.page_number, p.text) for p in pages]
        else:
            full_text, pages = load_docx(dest)
            page_pairs = [(p.page_number, p.text) for p in pages]

        offsets = build_page_offsets(page_pairs)
        contract.full_text = full_text
        contract.clauses = segment_clauses(contract_id, full_text, offsets)
        contract.status = ContractStatus.SEGMENTED
    except Exception as exc:
        logger.exception("Upload processing failed")
        contract.status = ContractStatus.FAILED
        contract.error_message = str(exc)
        store.save(contract)
        REQUESTS.labels(endpoint="upload", status="error").inc()
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    contract.updated_at = utcnow()
    store.save(contract)
    REQUESTS.labels(endpoint="upload", status="ok").inc()
    LATENCY.labels(endpoint="upload").observe(time.perf_counter() - start)

    return UploadResponse(
        id=contract.id,
        filename=contract.filename,
        status=contract.status.value,
        clause_count=len(contract.clauses),
    )


@app.post("/contracts/{contract_id}/analyze", dependencies=[Depends(require_internal_token)])
def analyze_contract(contract_id: str) -> AnalyzeResponse:
    start = time.perf_counter()
    contract = store.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if not contract.clauses:
        raise HTTPException(status_code=422, detail="Contract has no segmented clauses")

    try:
        run_analysis(contract)
        store.save(contract)
    except ValueError as exc:
        contract.status = ContractStatus.FAILED
        contract.error_message = str(exc)
        store.save(contract)
        REQUESTS.labels(endpoint="analyze", status="error").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        contract.status = ContractStatus.FAILED
        contract.error_message = str(exc)
        store.save(contract)
        REQUESTS.labels(endpoint="analyze", status="error").inc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    REQUESTS.labels(endpoint="analyze", status="ok").inc()
    LATENCY.labels(endpoint="analyze").observe(time.perf_counter() - start)
    return AnalyzeResponse(
        id=contract.id,
        status=contract.status.value,
        analyzed_clauses=len(contract.analyses),
    )


@app.get("/contracts/{contract_id}/report", dependencies=[Depends(require_internal_token)])
def get_report(contract_id: str) -> ReportSchema:
    contract = store.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    analyses = [_analysis_schema(a) for a in contract.analyses]
    discrepancies = [a for a in analyses if a.requires_priority_review]
    discrepancies.sort(key=lambda a: (0 if a.risk_level == "alto" else 1 if a.risk_level == "medio" else 2))

    return ReportSchema(
        id=contract.id,
        filename=contract.filename,
        status=contract.status.value,
        clauses=[_clause_schema(c) for c in contract.clauses],
        analyses=analyses,
        discrepancies=discrepancies,
    )


@app.get("/contracts/{contract_id}/clause/{clause_id}", dependencies=[Depends(require_internal_token)])
def get_clause(contract_id: str, clause_id: str) -> ClauseDetailSchema:
    contract = store.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    clause = next((c for c in contract.clauses if c.id == clause_id), None)
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found")

    analysis = next((a for a in contract.analyses if a.clause_id == clause_id), None)
    return ClauseDetailSchema(
        clause=_clause_schema(clause),
        analysis=_analysis_schema(analysis) if analysis else None,
    )
