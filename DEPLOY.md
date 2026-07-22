# Despliegue de demo: Vercel (frontend) + Render (backend + Postgres)

Monorepo: el frontend (React/Vite) va a Vercel; el backend (FastAPI, WebSockets,
scheduler in-process, Postgres) va a Render porque necesita un proceso de larga
duración (Vercel es serverless y no lo soporta). Ambos en plan **gratuito** — pensado
para una demo al cliente, no para producción final (ver limitaciones al final).

## 1. Backend en Render

**Opción rápida — Blueprint:** este repo trae `render.yaml` en la raíz. En Render:
"New" → "Blueprint" → seleccionar este repo → Render lee `render.yaml` y crea solo
el servicio web (`skynet-logistics-backend`, root `backend/`) y la base de datos
Postgres free (`skynet-logistics-db`) automáticamente, con `DATABASE_URL`,
`JWT_SECRET_KEY` y `GPS_CREDENTIALS_ENCRYPTION_KEY` autogenerados.

Si preferís crearlo a mano en vez del Blueprint:
1. "New" → "PostgreSQL" → plan **Free**. Copiar la "Internal Database URL".
2. "New" → "Web Service" → conectar el repo → **Root Directory**: `backend`.
   Runtime: Python. Build command: `pip install -r requirements.txt`. Start command:
   `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   Plan: **Free**.
3. Variables de entorno (ver `backend/.env.example` para la lista completa):
   - `DATABASE_URL` = la Internal Database URL del paso 1 (el config del backend
     ya normaliza `postgres://`/`postgresql://` a `postgresql+asyncpg://` solo,
     no hace falta editarla a mano)
   - `JWT_SECRET_KEY` (generar un valor random, no usar el de dev)
   - `GPS_CREDENTIALS_ENCRYPTION_KEY` (generar uno nuevo, ver el comentario en
     `.env.example`)
   - `CORS_ORIGINS` = por ahora `http://localhost:5173`, se actualiza en el
     paso 6 con la URL final de Vercel
   - `SEED_SUPERADMIN_EMAIL` / `SEED_SUPERADMIN_PASSWORD`
   - `ROUTING_ENGINE=fake` (no hay token de Mapbox todavía)

4. Deploy. El start command corre `alembic upgrade head` antes de levantar
   uvicorn, así que las migraciones se aplican solas en cada deploy.
5. Correr el seed inicial UNA vez (Render → servicio → pestaña "Shell") para
   crear la empresa "Platform" y el primer superadmin:
   ```
   python -m app.seed
   ```
6. Copiar la URL pública que asigna Render (`https://skynet-logistics-backend.onrender.com`)
   — se usa como `VITE_API_BASE_URL` en Vercel (paso siguiente).

## 2. Frontend en Vercel

1. Vercel → "Add New Project" → importar el mismo repo de GitHub.
2. **Root Directory**: `frontend`.
3. Framework preset: Vite (autodetectado). Build command: `npm run build`, output:
   `dist` (autodetectado también).
4. Variable de entorno: `VITE_API_BASE_URL` = la URL de Render del paso anterior
   (sin `/` final), ej. `https://skynet-logistics-backend.onrender.com`.
5. Deploy. `frontend/vercel.json` ya trae el rewrite a `index.html` para que las
   rutas de React Router (`/vehicles/:id`, etc.) no den 404 al refrescar.
6. Volver a Render y actualizar `CORS_ORIGINS` del backend con la URL final de
   Vercel (ej. `https://skynetlogistics.vercel.app`), redeploy.

## 3. Verificación

- `GET https://<backend>.onrender.com/health` → `{"status": "ok"}` (la primera
  request tras un rato inactivo tarda ~30-50s, ver limitaciones abajo)
- Login en `https://<frontend>.vercel.app/login` con el superadmin sembrado.
- Abrir el panel de despachador y el portal de conductor (chat) para confirmar
  que el WebSocket conecta (`wss://<backend>/api/v1/ws/...`).

## Limitaciones del plan gratuito (aceptable para demo, no para producción)

- **Render free duerme el servicio tras ~15 min sin tráfico**: la primera carga
  después de dormido tarda ~30-50s en responder (el resto, normal). Si vas a
  hacer la demo en vivo, abrí la app un par de minutos antes para "despertarla".
- **Postgres free de Render expira a los 90 días** y hay que recrearla (o pasar
  a un plan pago) — no es un problema para una demo puntual.
- **Uploads de adjuntos** (`backend/app/core/file_storage.py`, Fase 8): el
  filesystem de Render no persiste entre deploys/reinicios en el plan free. Los
  reportes de incidencia con adjuntos funcionan pero el archivo puede perderse
  si el servicio se reinicia — no crítico para mostrar el flujo en una demo.
- El scheduler in-process (alertas, fatiga, particiones GPS) se pausa mientras
  el servicio está dormido, y se re-arma solo al despertar — no pierde datos,
  solo no corre en tiempo real si nadie visita el sitio.

## Para pasar esto a producción real más adelante

Ver la sección de notas de diseño de `CLAUDE.md`: subir a un plan pago (Render
Starter o Railway Hobby) para evitar el sleep, agregar un volumen persistente
para `uploads/`, y token real de Mapbox si se necesita ruteo real en vez del
motor `fake`.
