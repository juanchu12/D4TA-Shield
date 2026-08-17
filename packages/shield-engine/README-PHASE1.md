# Fase 1 — Motor de análisis D4TA Shield

Motor FastAPI aislado: ingesta PDF/DOCX, segmentación por cláusulas, reglas deterministas + LLM, detección de discrepancias.

## Decisiones de diseño

1. **Segmentación estructural** — No chunking fijo. Se detectan límites por numeración contractual (`CLÁUSULA`, `ARTÍCULO`, `1.1`, etc.).
2. **Pipeline en dos capas** — Reglas regex primero (alta confianza en umbrales objetivos); LLM (`gpt-4o-mini`, temp 0) para categoría y severidad con cita textual obligatoria.
3. **Discrepancias nunca silenciadas** — Si regla y LLM difieren ≥2 niveles de severidad o categoría crítica, `requires_priority_review=true`.
4. **Sin veredicto agregado** — El reporte lista cláusulas individuales; no existe `overall_risk`.
5. **Persistencia SQLite** — Estado entre upload/analyze/report en Fase 1; Symfony será source of truth en Fase 2.
6. **Extracción cascada** — PyPDF → pdfplumber → PyMuPDF → OCR (tesseract) para escaneados.
7. **Auth interna** — Header `X-Internal-Token`; el frontend nunca llama al motor directamente.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/contracts/upload` | Sube y segmenta |
| POST | `/contracts/{id}/analyze` | Clasifica riesgo |
| GET | `/contracts/{id}/report` | Informe completo |
| GET | `/contracts/{id}/clause/{clause_id}` | Detalle de cláusula |
| GET | `/health` | Healthcheck |

## Desarrollo local

```bash
cd packages/shield-engine
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -e ".[dev]"
cp .env.example .env     # OPENAI_API_KEY
uvicorn shield_engine.api.main:app --reload --port 8080
pytest
```

## Tests

Fixtures sintéticas en `tests/conftest.py`. Nunca se usan contratos reales de clientes.
