# Despliegue D4TA Shield

Dos modos soportados. En ambos casos el motor Python (`shield-engine`) **nunca** se expone al frontend — solo Symfony lo llama con `X-Internal-Token`.

---

## Option A — Cloudflare Pages (frontend) + Proxmox (backend)

### 1. Build frontend → Cloudflare Pages

```bash
cd apps/web
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=https://api-shield.yourd4ta.com
npm install && npm run pages:build
npx wrangler pages deploy .open-next/assets --project-name=shield
```

GitHub Actions (`.github/workflows/deploy-web.yml`) automatiza esto en push a `main`.

### 2. Backend en Proxmox (VM Docker)

```bash
cd infra
cp ../.env.example .env
# Editar OPENAI_API_KEY, JWT_PASSPHRASE, INTERNAL_TOKEN, POSTGRES_PASSWORD
docker compose up --build -d shield-db shield-engine shield-api
# No levantar shield-web si el frontend va en CF Pages
```

Generar JWT antes del primer arranque:

```bash
mkdir -p ../apps/api/config/jwt
openssl genrsa -aes256 -passout pass:YOUR_PASSPHRASE -out ../apps/api/config/jwt/private.pem 4096
openssl rsa -pubout -in ../apps/api/config/jwt/private.pem -passin pass:YOUR_PASSPHRASE -out ../apps/api/config/jwt/public.pem
docker compose exec shield-api php bin/console doctrine:schema:update --force
docker compose exec shield-api php bin/console app:seed-demo
```

### 3. Nginx Proxy Manager — Proxy Hosts

| Dominio | Destino interno | SSL | Websockets |
|---------|-----------------|-----|------------|
| `api-shield.yourd4ta.com` | `VM_IP:8000` | Force SSL + Let's Encrypt | No |
| `shield.yourd4ta.com` | Cloudflare Pages (automático) | CF SSL | No |

**Verificar SSL API:** `curl -I https://api-shield.yourd4ta.com/api/health`

---

## Option B — Todo en un Docker Compose (VM Proxmox)

```bash
cd infra
cp ../.env.example .env
docker compose up --build -d
```

### NPM — Proxy Host único (o dos)

| Dominio | Puerto interno | Websockets |
|---------|----------------|------------|
| `shield.yourd4ta.com` | `VM_IP:3000` (shield-web) | No |
| `api-shield.yourd4ta.com` | `VM_IP:8000` (shield-api) | No |

`shield-engine` y `shield-db` **no** se publican — red Docker interna.

---

## Servicios

| Servicio | Contenedor | Puerto interno | Healthcheck |
|----------|------------|----------------|-------------|
| Frontend | `shield-web` | 3000 | `GET /` |
| Symfony API | `shield-api` | 8000 | `GET /api/health` |
| Motor Python | `shield-engine` | 8080 | `GET /health` |
| PostgreSQL | `shield-db` | 5432 | `pg_isready` |

---

## CI/CD (GitHub Actions)

| Workflow | Trigger | Acción |
|----------|---------|--------|
| `deploy-web.yml` | push `main` (apps/web) | Build + deploy Cloudflare Pages |
| `docker-build.yml` | push `main` | Build imágenes shield-api + shield-engine → registry |

En Proxmox, un webhook o script pull+compose recrea los contenedores tras push al registry.

---

## Checklist post-deploy

- [ ] `GET /api/health` → `"status":"ok"` y engine ok
- [ ] Login demo: `legal@demo.d4ta.local` / `legal123`
- [ ] Upload PDF → analyze → report con disclaimer
- [ ] Discrepancias visibles si regla ≠ LLM
- [ ] "Marcar como revisada" genera audit log

---

## Demo accounts (seed)

| Email | Password | Rol |
|-------|----------|-----|
| admin@demo.d4ta.local | admin123 | Admin + Legal |
| legal@demo.d4ta.local | legal123 | Legal |
| comercial@demo.d4ta.local | comercial123 | Comercial |
| readonly@demo.d4ta.local | readonly123 | Solo lectura |
