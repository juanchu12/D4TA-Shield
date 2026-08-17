# Fase 3 — Frontend Next.js D4TA Shield

UI con brand kit LegalTech (Deep Indigo `#6D5BFF`), glassmorphism y disclaimer legal persistente.

## Pantallas

- `/` — Landing
- `/login` — JWT por tenant
- `/dashboard` — Lista de contratos + upload
- `/contracts/[id]` — Documento con cláusulas resaltadas + panel lateral + botón "Marcar como revisada"
- `/discrepancies` — Comparador de discrepancias regla vs LLM

## Brand

- Color producto: `#6D5BFF` (sin gradiente D4TA madre)
- Severidad: ámbar (medio), coral (alto) — separado del indigo de marca
- Tipografías: Bricolage Grotesque, Plus Jakarta Sans, IBM Plex Mono

## Desarrollo

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

Build Cloudflare Pages: `npm run pages:build && npm run deploy`

## Decisiones

- Disclaimer visible en shell autenticado y en login — no descartable silenciosamente.
- "Marcar como revisada" solo en cláusulas de riesgo alto; genera auditoría en Symfony.
- Sin veredicto agregado de contrato en ninguna pantalla.
