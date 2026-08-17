# D4TA Shield (monorepo)

Analista de riesgo contractual — segunda lectura antes de la firma, no sustituto de asesoría legal.

| Package | Role |
|---------|------|
| [`packages/shield-engine`](packages/shield-engine) | FastAPI — extracción, segmentación, reglas + LLM |
| [`apps/api`](apps/api) | Symfony — tenants, JWT, auditoría, proxy al motor |
| [`apps/web`](apps/web) | Next.js 15 UI (Cloudflare Pages) |
| [`infra`](infra) | Docker Compose full stack |

## Product identity

- **Name:** D4TA Shield · **Category:** LEGALTECH · **Accent:** Deep Indigo `#6D5BFF`
- **Pipeline:** PDF/DOCX → cláusulas → reglas + LLM → discrepancias → revisión humana auditada

## Architecture

```
Cloudflare Pages (web) → Symfony API → FastAPI engine
                              └─ PostgreSQL
```

## Quick start (local)

### 1. Motor Python

```bash
cd packages/shield-engine
python -m venv .venv && .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn shield_engine.api.main:app --reload --port 8080
pytest
```

### 2. Symfony API

```bash
cd apps/api
composer install
cp .env.example .env
php bin/console doctrine:schema:update --force
php bin/console app:seed-demo
php -S 0.0.0.0:8000 -t public
```

### 3. Frontend

```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

### Full stack Docker

```bash
cd infra && cp ../.env.example .env && docker compose up --build
```

**Deploy:** [README-DEPLOY.md](README-DEPLOY.md)

## Phase READMEs

- [Fase 1 — Motor](packages/shield-engine/README-PHASE1.md)
- [Fase 2 — Symfony](apps/api/README-PHASE2.md)
- [Fase 3 — Frontend](apps/web/README-PHASE3.md)
