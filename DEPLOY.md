# Despliegue: Vercel (frontend) + Railway (backend + Postgres)

Monorepo: el frontend (React/Vite) va a Vercel; el backend (FastAPI, WebSockets,
scheduler in-process, Postgres) va a Railway porque necesita un proceso de larga
duración (Vercel es serverless y no lo soporta).

## 1. Backend en Railway

1. Crear proyecto en Railway → "Deploy from GitHub repo" → seleccionar este repo.
2. **Root Directory**: `backend` (Settings → General → Root Directory). Railway
   detecta Python (Nixpacks) y usa `backend/railway.json` para build/start.
3. Agregar un servicio **PostgreSQL** desde el mismo proyecto Railway (botón "+ New"
   → Database → PostgreSQL). Railway expone `DATABASE_URL` automáticamente, pero
   con el driver `postgresql://`; hay que convertirla a asyncpg:
   - Variable `DATABASE_URL` del servicio backend =
     `postgresql+asyncpg://` + el resto de la URL que da el plugin de Postgres
     (host/puerto/user/pass/db), o simplemente referenciar
     `${{Postgres.DATABASE_URL}}` y anteponer el driver en una variable propia.
4. Variables de entorno del servicio backend (Settings → Variables), ver
   `backend/.env.example` para la lista completa. Como mínimo:
   - `DATABASE_URL` (asyncpg, ver punto 3)
   - `JWT_SECRET_KEY` (generar uno nuevo, no usar el de dev)
   - `CORS_ORIGINS` = la URL de Vercel una vez creada (paso 2), ej.
     `https://skynetlogistics.vercel.app`
   - `SEED_SUPERADMIN_EMAIL` / `SEED_SUPERADMIN_PASSWORD`
   - `GPS_CREDENTIALS_ENCRYPTION_KEY` (generar uno nuevo por entorno, ver el
     comentario en `.env.example`)
   - `ROUTING_ENGINE=fake` hasta tener token de Mapbox (`MAPBOX_ACCESS_TOKEN`)
5. Deploy. `backend/railway.json` corre `alembic upgrade head` antes de levantar
   uvicorn, así que las migraciones se aplican solas en cada deploy.
6. Una vez arriba, correr el seed inicial UNA vez (Railway → servicio → pestaña
   "Shell" o `railway run python -m app.seed`) para crear la empresa "Platform" y
   el primer superadmin.
7. **Uploads de adjuntos** (`backend/app/core/file_storage.py`, Fase 8): Railway no
   persiste el filesystem entre deploys por defecto. Si vas a usar reportes de
   incidencia con adjuntos en producción, agregar un **Volume** en Railway montado
   en `uploads/` (Settings → Volumes), o migrar a un bucket S3-compatible más
   adelante (el código ya está aislado a ese único archivo).
8. Copiar la URL pública que asigna Railway (`https://<algo>.up.railway.app`) —
   se usa como `VITE_API_BASE_URL` en Vercel.

## 2. Frontend en Vercel

1. Vercel → "Add New Project" → importar el mismo repo de GitHub.
2. **Root Directory**: `frontend`.
3. Framework preset: Vite (autodetectado). Build command: `npm run build`, output:
   `dist` (autodetectado también).
4. Variable de entorno: `VITE_API_BASE_URL` = la URL de Railway del paso anterior
   (sin `/` final), ej. `https://skynetlogistics-backend.up.railway.app`.
5. Deploy. `frontend/vercel.json` ya trae el rewrite a `index.html` para que las
   rutas de React Router (`/vehicles/:id`, etc.) no den 404 al refrescar.
6. Una vez desplegado, volver a Railway y actualizar `CORS_ORIGINS` con la URL
   final de Vercel (paso 4 de la sección backend).

## 3. Verificación

- `GET https://<backend>/health` → `{"status": "ok"}`
- Login en `https://<frontend>/login` con el superadmin sembrado en el paso 6.
- Abrir el panel de despachador y el portal de conductor (chat) para confirmar
  que el WebSocket conecta (`wss://<backend>/api/v1/ws/...`) — revisar la consola
  del navegador si no conecta (revisar `CORS_ORIGINS` y que Railway exponga el
  servicio por HTTPS, lo hace por defecto).

## Notas

- El scheduler in-process (alertas, fatiga, particiones GPS) corre dentro del
  mismo proceso de uvicorn en Railway — no necesita un worker aparte porque
  Railway mantiene el proceso vivo (a diferencia de Vercel serverless).
- Si más adelante se agrega más de una instancia del backend, el
  `ConnectionManager` de WebSockets en memoria y el `AsyncIOScheduler` dejan de
  ser suficientes (duplicarían jobs / no compartirían conexiones) — ver las notas
  de diseño en `CLAUDE.md`.
