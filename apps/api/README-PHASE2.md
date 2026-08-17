# Fase 2 — Backend Symfony D4TA Shield

API multi-tenant con JWT que envuelve al motor Python. El frontend nunca llama al engine directamente.

## Entidades

| Entidad | Propósito |
|---------|-----------|
| `Tenant` | Organización cliente |
| `User` | Roles: legal, comercial, solo lectura, admin |
| `Contract` | Metadata del borrador + estado de análisis |
| `RiskFlag` | Cláusula señalada vinculada al contrato |
| `AuditLog` | Evidencia de revisión humana |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/login_check` | JWT (username=email) |
| GET | `/api/health` | Healthcheck |
| GET | `/api/contracts` | Lista por tenant |
| POST | `/api/contracts` | Upload PDF/DOCX |
| POST | `/api/contracts/{id}/analyze` | Ejecuta análisis |
| GET | `/api/contracts/{id}/report` | Informe completo |
| GET | `/api/contracts/{id}/discrepancies` | Solo discrepancias |
| POST | `/api/contracts/{id}/flags/{flagId}/review` | Marcar cláusula revisada (auditoría) |

## Setup local

```bash
cd apps/api
composer install
cp .env.example .env
# Generar JWT: openssl genrsa -out config/jwt/private.pem -aes256 4096
# openssl rsa -pubout -in config/jwt/private.pem -out config/jwt/public.pem
php bin/console doctrine:schema:update --force
php bin/console app:seed-demo
php -S 0.0.0.0:8000 -t public
```

## Decisiones

- Symfony es source of truth para tenants, usuarios y auditoría de revisión humana.
- `EngineClient` proxy autenticado con `X-Internal-Token`.
- Toda respuesta de análisis incluye disclaimer legal en el payload.
- Marcar cláusula como revisada siempre genera entrada en `AuditLog`.
