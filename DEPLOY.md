# Despliegue de demo: Vercel (frontend) + Render (backend) + Neon (Postgres)

Monorepo: el frontend (React/Vite) va a Vercel; el backend (FastAPI, WebSockets,
scheduler in-process) va a Render porque necesita un proceso de larga duración
(Vercel es serverless y no lo soporta). Todos en plan **gratuito** — pensado para
una demo al cliente, no para producción final (ver limitaciones al final).

**Por qué Neon y no la Postgres free de Render:** la Postgres free de Render
**expira a los 90 días** y se borra sin aviso (fue justo lo que pasó — ver
histórico del proyecto). Neon free no tiene ese límite de expiración (solo
suspende el cómputo tras inactividad, pero los datos no se pierden y despierta
solo en la siguiente conexión).

## 0. Base de datos en Neon

1. Crear cuenta gratis en [neon.tech](https://neon.tech), crear un proyecto.
2. Copiar la **connection string** que ofrece Neon — usar la de **conexión
   directa**, no la "pooled" (PgBouncer en modo transacción rompe los prepared
   statements que usa `asyncpg`).
3. La URL trae `?sslmode=require` — no hace falta editarla a mano:
   `backend/app/core/config.py::_use_asyncpg_driver` ya la traduce a `ssl=require`
   (el kwarg que sí entiende `asyncpg`) y normaliza `postgres://`/`postgresql://`
   a `postgresql+asyncpg://`.

## 1. Backend en Render

**Opción rápida — Blueprint:** este repo trae `render.yaml` en la raíz. En Render:
"New" → "Blueprint" → seleccionar este repo → Render lee `render.yaml` y crea el
servicio web (`skynet-logistics-backend`, root `backend/`) con `JWT_SECRET_KEY` y
`GPS_CREDENTIALS_ENCRYPTION_KEY` autogenerados. `DATABASE_URL` queda como variable
manual (`sync: false`) — completarla a mano en el dashboard con la connection
string de Neon del paso 0.

Si preferís crearlo a mano en vez del Blueprint:
1. "New" → "Web Service" → conectar el repo → **Root Directory**: `backend`.
   Runtime: Python. Build command: `pip install -r requirements.txt`. Start command:
   `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   Plan: **Free**.
2. Variables de entorno (ver `backend/.env.example` para la lista completa):
   - `DATABASE_URL` = la connection string de Neon del paso 0
   - `JWT_SECRET_KEY` (generar un valor random, no usar el de dev)
   - `GPS_CREDENTIALS_ENCRYPTION_KEY` (generar uno nuevo, ver el comentario en
     `.env.example`)
   - `CORS_ORIGINS` = por ahora `http://localhost:5173`, se actualiza en el
     paso 6 de la sección de Vercel con la URL final
   - `SEED_SUPERADMIN_EMAIL` / `SEED_SUPERADMIN_PASSWORD`
   - `ROUTING_ENGINE=fake` (no hay token de Mapbox todavía)
3. Deploy. El start command corre `alembic upgrade head && python -m app.seed`
   antes de levantar uvicorn, así que migraciones y seed se aplican solos en
   cada deploy (no hace falta entrar a la "Shell" — el plan free de Render no
   la tiene).
4. Copiar la URL pública que asigna Render (`https://skynet-logistics-backend.onrender.com`)
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
- **Neon free suspende el cómputo tras inactividad** (no borra datos): la
  primera query tras un rato sin uso tarda un par de segundos extra mientras
  despierta — no requiere acción manual, a diferencia de la Postgres free de
  Render que usábamos antes (esa sí expiraba a los 90 días y se borraba).
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
