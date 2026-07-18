# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Sistema de Gestión de Flota (Fleet Management System)

### Contexto del proyecto

Sistema web de gestión de flotas de transporte terrestre, inspirado en TRANSPORTEX pero con
diferenciadores propios: integración multi-proveedor GPS, optimización de rutas en tiempo real
y cálculo de fatiga del conductor. Producto destinado a venta por cliente instalado o SaaS
multiempresa para el mercado latinoamericano (Venezuela, Colombia, México inicialmente).

## Estado actual

- **Fase 0 (Core: auth multiempresa, usuarios/roles): completa.** Backend probado (24 tests,
  pytest + Postgres real) y frontend verificado end-to-end (login, layout con sidebar,
  gestión de usuarios) contra el backend real.
- **Fase 1 (Mantenimiento + Alertas): completa.** Backend probado (49 tests en total, 25 nuevos
  de esta fase) y frontend verificado end-to-end en navegador (vehículos, conductores, detalle
  de vehículo con historial de mantenimiento, programación/cierre de tareas, panel de alertas
  con badge en el sidebar).
- **Fase 2 (Control de viajes): completa.** Backend probado (71 tests en total, 22 nuevos de esta
  fase, incluida la fórmula de nómina reproducida exactamente contra el ejemplo numérico aprobado)
  y frontend verificado end-to-end en navegador (viajes con sugerencia automática de flete/distancia,
  inicio/gastos/cierre de viaje, tabulados de configuración, documentos imprimibles).
- **Fase 3 (Integración GPS/Telemetría): completa.** Backend probado (90 tests en total, 19 nuevos
  de esta fase) y frontend verificado end-to-end en navegador (configuración de proveedor GPS con
  token de webhook, mapeo de vehículo a device externo, ingesta simulada vía webhook, mapa en vivo
  de la flota y replay histórico de ruta con Leaflet).
- **Fase 4 (Fatiga del conductor): completa.** Backend probado (116 tests en total, 26 nuevos de
  esta fase, incluida la fórmula de riesgo reproducida exactamente contra el ejemplo numérico
  aprobado) y frontend verificado end-to-end en navegador (reglas de fatiga configurables, badge
  de nivel de riesgo en el listado de conductores, detalle de conductor con historial/gráfico de
  risk_score, advertencia no bloqueante al crear un viaje con conductor en riesgo alto/crítico,
  alerta generada automáticamente y visible en el panel de alertas).
- **Fase 5 (Neumáticos): completa.** Backend probado (144 tests en total, 28 nuevos de esta fase)
  y frontend verificado end-to-end en navegador (alta de neumáticos, almacenes mínimos, diagrama
  de ejes por vehículo con instalación/desinstalación/envío a reparación-reencauche/retorno de
  taller vía clic en posición, movimiento en lote, cálculo de km por período y acumulado, alerta
  de disparidad de espesor entre neumáticos "morocha" con umbral configurable, reporte de
  rendimiento por marca/modelo).
- Próxima fase: **Fase 6 (Inventario/repuestos)** — sin iniciar, pendiente de propuesta de
  esquema/endpoints y aprobación antes de generar código (ver regla 1).

## Comandos de desarrollo

### Backend (`backend/`)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # ajustar DATABASE_URL/JWT_SECRET_KEY si aplica

alembic upgrade head                 # aplica migraciones a la DB de DATABASE_URL
python -m app.seed                   # crea empresa "Platform", rol Superadmin y el primer usuario

uvicorn app.main:app --reload --port 8000   # dev server
python -m pytest -v                          # suite completa (requiere Postgres real, no sqlite)
```

Las migraciones nuevas se generan con `alembic revision --autogenerate -m "mensaje"` después de
editar los modelos en `app/models/`; siempre revisar el archivo generado antes de aplicarlo.

Los tests usan una base Postgres real (`fleet_test_db` en `tests/conftest.py`, no SQLite) porque
el modelo depende de tipos nativos de Postgres (UUID, JSONB). Debe existir y tener las
migraciones aplicadas (`DATABASE_URL=postgresql+asyncpg://.../fleet_test_db alembic upgrade head`)
antes de correr `pytest`.

### Frontend (`frontend/`)

```bash
cd frontend
npm install
npm run dev          # servidor Vite en :5173, con proxy /api -> backend en :8000
npx tsc -b           # type-check
npm run build         # build de producción
```

## Stack técnico

- **Backend:** FastAPI (Python) — async, pydantic para validación
- **Frontend:** React + Vite + TailwindCSS
- **Base de datos:** PostgreSQL + extensión TimescaleDB (hypertables para datos GPS/series temporales)
- **Auth:** JWT + RBAC (roles por módulo, multiempresa)
- **Motor de ruteo:** OSRM self-hosted (fase posterior)
- **Optimización VRP:** Google OR-Tools (fase posterior)
- **Colas/jobs:** para ingesta GPS y cálculo de alertas (ej. Celery + Redis, o APScheduler si el volumen es bajo al inicio)

## Reglas de trabajo con Claude Code

1. No escribir código sin aprobación explícita del spec de cada fase.
2. Cada fase se desarrolla, se revisa, se aprueba, y se hace `/clear` antes de iniciar la siguiente.
3. Reutilizar patrones y componentes ya definidos en fases anteriores (no reinventar).
4. Toda tabla nueva debe declarar sus relaciones (FK) explícitamente antes de generar migraciones.
5. Estética: dark-mode premium, tipografía serif para display, acentos oro/cobre (según guía de marca Wise Designs+).

## Arquitectura implementada

### Backend (`backend/app/`)

Capas separadas por responsabilidad, seguidas por todas las fases:
`models/` (SQLAlchemy async) → `schemas/` (Pydantic, request/response) → `crud/` (acceso a datos,
recibe siempre `company_id` explícito) → `api/v1/` (routers FastAPI, resuelven permisos e inyectan
`company_id` desde el JWT, nunca desde el payload del cliente).

- **Multiempresa (row-level):** cada tabla de negocio tiene `company_id`; toda query de `crud/`
  la recibe como parámetro obligatorio — nunca se filtra "opcionalmente". El superadmin no tiene
  bypass implícito: `companies` es el único recurso cross-tenant (ver `api/v1/companies.py`); el
  resto de endpoints quedan acotados a `current_user.company_id`, superadmin incluido.
- **RBAC:** `app/core/deps.py::require_permission(module, action)` es la dependency que protegen
  los routers. Superadmin (`is_superadmin=True`) pasa cualquier check. Los permisos viven en
  `roles.permissions` (JSONB `{modulo: [acciones]}`), ver `app/utils/permissions.py`. Los roles de
  Fase 0 no reciben automáticamente los módulos nuevos de fases posteriores — hay que asignarlos
  explícitamente al rol correspondiente.
- **Motor de alertas (`app/jobs/`):** `app/jobs/alerts.py::run_alert_checks(db, today=...)` es una
  función pura (recibe la sesión, no crea la suya) para poder invocarla directo desde tests sin
  levantar el scheduler. Se registra en `app/main.py` vía `AsyncIOScheduler` (APScheduler) dentro
  del `lifespan` de FastAPI — un solo proceso in-process, sin Celery/Redis. El anti-duplicado de
  alertas se resuelve con un índice único parcial en Postgres (`uq_alerts_unread_dedupe`, WHERE
  `status='no_leida'`) + `INSERT ... ON CONFLICT DO NOTHING` (ver `crud/alert.py::create_if_not_exists`);
  este patrón es el que hay que replicar para cualquier alerta nueva en fases futuras (fatiga,
  documentos vencidos, etc.), no reinventar la deduplicación en cada módulo.
- **Cálculos de negocio (`app/services/`):** lógica de negocio con fórmulas (nómina, flete, y lo
  que venga en fases futuras como fatiga) vive en funciones puras fuera de `crud/` y `api/`, para
  que el endpoint de "preview" (ej. `GET /trips/{id}/close-preview`) y el que persiste (`POST
  .../close`) compartan exactamente el mismo cálculo — ver `app/services/trip_calculations.py`.
- **Reutilizar jobs entre fases sin duplicar lógica:** cuando una fase nueva necesita re-disparar
  algo que ya hace un job de una fase anterior (ej. Fase 2 revalida mantenimiento por km al cerrar
  un viaje), se extiende la función existente con un parámetro opcional que acota su alcance
  (`run_alert_checks(db, vehicle_ids=[...])`) en vez de escribir una copia — el comportamiento por
  defecto (sin el parámetro) se mantiene idéntico para el job programado.
- **Auth:** access token JWT de corta vida (`app/core/security.py`); refresh token opaco
  (`secrets.token_urlsafe`) cuyo hash SHA-256 se guarda en `refresh_tokens` — rota en cada uso
  (`/auth/refresh` revoca el anterior y emite uno nuevo). Password con bcrypt.
- **`Base.__mapper_args__ = {"eager_defaults": True}`** (`app/core/database.py`) es necesario en
  todo modelo nuevo con columnas `server_default`/`onupdate`: sin esto, leer esas columnas tras un
  flush en modo async revienta con `MissingGreenlet`.
- **Seed:** `app/seed.py` crea la empresa "Platform", el rol de sistema "Superadmin" y el primer
  usuario superadmin — es el único punto de entrada para crear el primer usuario del sistema.
- **Adaptadores de proveedores externos (`app/gps_adapters/`):** para integrar un proveedor GPS
  nuevo (o cualquier otro proveedor externo en fases futuras con el mismo patrón) se implementa
  `GPSProviderAdapter.normalize()` + una entrada en `ADAPTER_REGISTRY` — la ingesta (webhook/polling),
  los endpoints y el resto del sistema no se tocan. El primer adapter (`TrakerGPSAdapter`) usa un
  payload de ejemplo no confirmado contra la doc real del proveedor; ajustar solo ese archivo
  cuando se valide.
- **Credenciales de proveedores externos:** nunca en texto plano — se encriptan con Fernet
  (`app/core/encryption.py`, clave en `GPS_CREDENTIALS_ENCRYPTION_KEY`) antes de persistir. Mismo
  criterio a aplicar a cualquier credencial de terceros en fases futuras.
- **Webhooks públicos:** el único endpoint sin JWT de todo el sistema es
  `POST /api/v1/gps/webhook/{provider_id}` — se autentica con un token propio (hash SHA-256 en
  `gps_providers.webhook_token_hash`, mismo patrón que los refresh tokens), no con el auth de
  usuarios. Cualquier webhook público futuro debe seguir este mismo esquema de token dedicado.
- **Tablas particionadas (`vehicle_positions`):** particionado nativo de Postgres por rango
  mensual de `timestamp` (no TimescaleDB — hosting no confirmado; el esquema es compatible con
  una futura migración a hypertable sin cambios). Las particiones se crean en la migración
  (mes actual + 2 siguientes) y `app/jobs/gps_partitions.py` asegura mensualmente que siempre
  exista la partición de 3 meses a futuro, corrido por el mismo `AsyncIOScheduler` de Fase 1.
- **`app/services/vehicle_odometer.py::advance_odometer`** centraliza "si el odómetro nuevo es
  mayor al actual, actualizar vehículo + re-chequear mantenimiento" — lo usa tanto el cierre de
  viaje (Fase 2) como la ingesta GPS (Fase 3). Cualquier fuente nueva de lecturas de odómetro debe
  llamar esta función en vez de repetir el patrón.
- **Cálculo de fatiga (`app/services/fatigue_calculations.py`):** reconstruye ventanas de manejo
  continuo a partir de `vehicle_positions.ignition_status` (tolerancia de hueco de 15 min entre
  lecturas; una lectura de más de 30 min de antigüedad ya no cuenta como "manejando ahora") y cae a
  `trips.started_at/ended_at` cuando el conductor no tiene vehículo asignado o no hay datos GPS —
  mismo patrón de "GPS primero, trips como fallback" a reutilizar si una fase futura necesita otra
  señal de actividad del conductor. La fórmula de riesgo (`calculate_risk`) usa el `max()` de las
  razones continua/24h/7 días (no el promedio) multiplicado por un factor de manejo nocturno, capado
  en 150; los 4 niveles (`bajo/medio/alto/critico`) son fijos y no calzan 1:1 con los 3 niveles de
  severidad de `alerts` (Fase 1) — ver `RISK_LEVEL_TO_SEVERITY` en `app/jobs/fatigue.py`.
- **Job de fatiga (`app/jobs/fatigue.py::run_fatigue_checks`):** corre cada 30 min vía el mismo
  `AsyncIOScheduler`, recorre conductores con `status="activo"`, cachea `FatigueRule` por
  `company_id` dentro de la corrida, hace upsert en `driver_fatigue_logs` (`UNIQUE(driver_id, date)`,
  `ON CONFLICT DO UPDATE`) y genera alertas de riesgo alto/crítico reutilizando
  `crud/alert.py::create_if_not_exists` (Fase 1) — sin lógica nueva de deduplicación, tal como exige
  el patrón ya establecido.
- **Endpoint de fatiga por conductor separado de `trips`:** `GET /drivers/{id}/fatigue-status` es
  un endpoint de solo consulta que el frontend llama al armar el formulario de viaje para mostrar
  una advertencia no bloqueante — `POST /trips` en sí no valida ni bloquea por fatiga, a propósito.
- **`axle_position` modelado como 3 columnas estructuradas** (`axle_number` SmallInt, `axle_side`
  izquierdo/derecho/unico, `axle_dual_position` unico/interior/exterior) en vez de un código de
  texto libre — permite detectar el par "morocha" (mismo `vehicle_id`+`axle_number`+`axle_side`,
  `axle_dual_position` distinto) con una query directa, sin parsear strings. Mismas 3 columnas se
  repiten como snapshot en `tire_movements` para el historial.
- **`app/services/tire_movements.py::apply_movement`** centraliza la transición de estado de un
  neumático (instalación/desinstalación/envío a reparación-reencauche/retorno de taller): valida el
  estado origen, resuelve `km_at_movement` desde `vehicles.current_odometer_km`, actualiza `tires` y
  crea el registro en `tire_movements` de forma atómica — lo usan tanto el endpoint individual como
  el de lote (`POST /tire-movements/batch`), mismo patrón que `vehicle_odometer.py::advance_odometer`.
- **Detección de disparidad no es un job nuevo:** extiende `run_alert_checks(db, vehicle_ids=...)`
  (`app/jobs/alerts.py`) con un chequeo adicional que agrupa neumáticos `instalado` por posición
  "morocha" y genera alerta `tire_disparity` (`entity_type="tire"`, `entity_id` = el neumático con
  menor espesor del par) si la diferencia supera `tire_settings.disparity_threshold_mm` — reutiliza
  `create_if_not_exists` (Fase 1) para el anti-duplicado, tal como exige el patrón ya establecido.
  Se dispara scoped a un vehículo tras cada movimiento/edición de espesor, y también en el barrido
  diario completo.
- **`app/services/tire_km.py`** (`close_periods`/`calculate_tire_km`/`compute_performance`) empareja
  cada movimiento `instalacion` con el siguiente que lo cierra (desinstalación o envío a
  reparación/reencauche) a partir de `km_at_movement` — es la única lógica de cálculo de km, la
  reutilizan tanto el detalle de neumático (km del período actual + acumulado) como la analítica de
  rendimiento por marca/modelo (`GET /tires/analytics/performance`), sin duplicar el emparejamiento.
- **`warehouses`** es la versión mínima acordada para esta fase (`id, company_id, name, location`) —
  Fase 6 (Inventario) la extiende sin romper Fase 5.

### Frontend (`frontend/src/`)

Organización por *feature*, no por tipo de archivo: `features/<dominio>/{api.ts,hooks.ts}` para
llamadas HTTP y estado; `routes/` son las pantallas; `layouts/` es el shell (`AuthLayout` para
login, `DashboardLayout` con `Sidebar` para el resto); `components/ui/` son primitivas reusables
(`Button`, `Input`, `Modal`, `Badge`); `components/<dominio>/` son componentes específicos de un
feature (ej. `components/users/UserTable.tsx`).

- **Auth:** `features/auth/AuthContext.tsx` guarda `user` + `permissions` en memoria; los tokens
  viven en `localStorage` (`lib/axios.ts`). El interceptor de respuesta reintenta una vez con
  refresh automático ante un 401 y, si falla, limpia tokens y redirige a `/login`.
- **Permisos en UI:** `useAuth().hasPermission(module, action)` — replica la misma lógica que el
  backend (superadmin siempre `true`, si no busca en `permissions[module]`). Gatea botones/acciones,
  no reemplaza la validación del backend.
- **Sidebar:** ya lista para las fases futuras — los módulos no implementados aparecen listados y
  deshabilitados bajo "Próximamente" en vez de omitirse, para no rehacer el layout en cada fase.
- **Tailwind v4:** tema (colores oro/cobre, fuente serif de display) definido vía `@theme` en
  `src/styles/index.css`, no en `tailwind.config.*` — es el patrón nativo de Tailwind v4.
- **Pantallas de configuración sin ruta propia en el sidebar:** siguiendo el mismo patrón que
  `trip-settings` (Fase 2) y `gps-settings` (Fase 3), `fatigue-settings` no tiene entrada directa en
  el `Sidebar` — se accede vía un botón "Reglas de fatiga" dentro de `DriversPage`. El detalle de
  conductor (`/drivers/:driverId`, con historial/gráfico de `risk_score`) se llega haciendo click en
  el nombre del conductor en `DriverTable`.
- **Advertencia de fatiga en creación de viaje:** `TripFormModal` llama a
  `useDriverFatigueStatus(driverId)` (que pega contra `GET /drivers/{id}/fatigue-status`) cada vez
  que cambia el conductor seleccionado y muestra un mensaje no bloqueante si el nivel es alto/crítico
  — el formulario sigue siendo enviable, solo advierte.
- **Gráfico de historial de fatiga:** `DriverDetailPage` dibuja un bar chart simple con divs/CSS
  (sin librería de gráficos nueva), coloreado por `risk_level`, igual de simple que el resto de
  visualizaciones del proyecto (mapa GPS es la única que usa una librería externa, Leaflet).
- **`VehicleAxleDiagram`** (`components/tires/`) infiere el layout de ejes a partir de los
  neumáticos ya instalados en el vehículo (más un layout base sugerido por `vehicle.type` cuando no
  hay ninguno instalado todavía — eje 1 direccional simple, resto doble rodado) en vez de agregar un
  campo de configuración de ejes a `vehicles` — divs/CSS coloreados por posición, mismo criterio
  "sin librería nueva" que el resto del proyecto. Clic en una posición vacía abre `InstallTireModal`
  (elige un neumático de almacén); clic en una posición ocupada abre `TireMovementModal` acotado a
  los movimientos válidos para el estado actual de ese neumático.
- **`tire-settings`, `warehouses` y `tire-performance` sin ruta propia en el `Sidebar`:** siguiendo
  el mismo patrón que `trip-settings`/`gps-settings`/`fatigue-settings`, se acceden vía botones
  secundarios en `TiresPage`. `Neumáticos` sí tiene entrada directa en el `Sidebar` (reemplaza el
  placeholder de "Próximamente"); el diagrama por vehículo se llega desde `VehicleDetailPage` con un
  link "Neumáticos", igual que "Ver ruta GPS" (Fase 3).

---

## Modelo de datos — Entidades principales

### Núcleo / Multiempresa
- **companies** — id, name, tax_id, plan, created_at
- **users** — id, company_id (FK), name, email, password_hash, role, active
- **roles** — id, name, permissions (JSON por módulo)

### Gestión de Vehículos
- **vehicles** — id, company_id, plate, brand, model, year, vin, type (camión/remolque/cabezal), status, current_odometer_km, assigned_driver_id (FK)
- **drivers** — id, company_id, name, license_number, license_expiry, phone, status

### Mantenimiento
- **maintenance_tasks** — id, vehicle_id, type (preventivo/correctivo), scheduled_by (tiempo/km), due_date, due_km, status, responsible_id
- **maintenance_records** — id, task_id, cost_labor, cost_parts, provider_id, completed_at, notes
- **providers** — id, company_id, name, type, contact_info

### Control de Viajes
- **trips** — id, vehicle_id, driver_id, trailer_id, origin, destination, distance_km, cargo_type, status, started_at, ended_at
- **trip_expenses** — id, trip_id, concept (combustible, peaje, viáticos, etc.), amount
- **trip_payroll** — id, trip_id, base_salary, bonuses, advance_payment, total_to_pay

### Neumáticos
- **tires** — id, company_id, unique_code, brand, model, current_thickness_mm, status
  (instalado/almacen/reparacion), vehicle_id (nullable), axle_number/axle_side/axle_dual_position
  (nullable, ver notas de diseño de axle_position), warehouse_id (nullable)
- **tire_movements** — id, company_id, tire_id, movement_type
  (instalacion/desinstalacion/envio_reparacion/envio_reencauche/retorno_taller), vehicle_id
  (nullable, snapshot), axle_number/axle_side/axle_dual_position (nullable, snapshot),
  warehouse_id (nullable), provider_id (nullable), km_at_movement (nullable), thickness_mm
  (nullable), notes, recorded_by, created_at
- **tire_settings** — id, company_id (unique), disparity_threshold_mm — umbral configurable del
  motor de disparidad, mismo patrón que `fatigue_rules` (Fase 4)
- **warehouses** — id, company_id, name, location — versión mínima introducida en Fase 5 (ver
  Inventario más abajo); Fase 6 la extiende sin romper Fase 5

### Inventario
- **warehouses** — ver Neumáticos (Fase 5); Fase 6 le agrega los campos que necesite sin romper la
  compatibilidad con `tires`/`tire_movements`
- **inventory_items** — id, warehouse_id, sku, name, quantity, min_stock, unit_cost
- **inventory_movements** — id, item_id, vehicle_id (nullable), type (entrada/salida), quantity, reference_doc

### GPS / Telemetría (hypertable — TimescaleDB)
- **gps_providers** — id, company_id, provider_name, api_credentials (encriptado), adapter_type
- **vehicle_positions** (hypertable) — vehicle_id, timestamp, lat, lng, speed_kmh, odometer_km, ignition_status, heading
- **gps_provider_vehicle_map** — vehicle_id, provider_id, external_device_id

### Optimización de rutas
- **route_plans** — id, trip_id, origin_coords, destination_coords, waypoints (JSON), calculated_distance_km, calculated_duration_min, engine_used
- **route_recalculations** — id, route_plan_id, reason (desvío/tráfico), timestamp, new_route_data

### Fatiga del conductor
- **fatigue_rules** — id, company_id, max_continuous_hours, max_24h_hours, max_7day_hours, night_driving_weight
- **driver_fatigue_logs** — id, driver_id, date, continuous_driving_min, total_24h_min, total_7day_min, night_driving_min, risk_score, risk_level

### Módulos auxiliares
- **documents** — id, entity_type (vehicle/driver), entity_id, doc_type, expiry_date, file_url
- **alerts** — id, company_id, type, entity_type, entity_id, message, severity, status, created_at
- **fuel_logs** — id, vehicle_id, trip_id (nullable), liters, cost, odometer_km, timestamp
- **closures** — id, company_id, period_start, period_end, locked_by, locked_at

---

## Fases de desarrollo

| Fase | Módulo | Depende de |
|---|---|---|
| 0 | Core: auth multiempresa, vehículos, usuarios/roles | — |
| 1 | Mantenimiento + motor de alertas | Fase 0 |
| 2 | Control de viajes (cálculos financieros/tabulados) | Fase 0 |
| 3 | Integración GPS (adaptador + ingesta + hypertable) | Fase 0 |
| 4 | Fatiga del conductor (reglas sobre datos GPS + viajes) | Fase 2, 3 |
| 5 | Neumáticos | Fase 1 |
| 6 | Inventario/repuestos | Fase 1 |
| 7 | Optimizador de rutas (OSRM → luego OR-Tools para VRP) | Fase 3 |
| 8 | Reportes/BI + exportaciones (Excel/HTML/XML) | Todas las anteriores |
| 9 | Módulos auxiliares finales (documentos, cierres administrativos) | Fase 0 |

---

## Notas de diseño de la integración GPS

- Interfaz común `GPSProviderAdapter` con método `normalize(raw_payload) -> VehiclePosition`.
- Primer proveedor a integrar: (definir — pendiente de decisión).
- Ingesta por webhook si el proveedor lo soporta; fallback a polling programado.
- Guardar siempre el payload crudo además del normalizado (auditoría/debug).

## Notas de diseño de fatiga del conductor

- Basado en reglas de horas de servicio, no en sensores biométricos (viable sin hardware adicional).
- Se alimenta de: tiempo de ignición encendida (GPS) + registros de viajes.
- Score configurable por empresa vía `fatigue_rules`.
- Alertas de riesgo alto/crítico se integran con el módulo de `alerts` existente, notificando al despachador antes de asignar un nuevo viaje.

## Notas de diseño de neumáticos

- `axle_position` no es un campo de configuración de vehículo: el diagrama se arma dinámicamente
  a partir de los neumáticos instalados (más una heurística de layout por `vehicle.type` cuando el
  vehículo todavía no tiene ninguno), así que soporta cualquier configuración de ejes sin migración.
- El ciclo de vida de un neumático es lineal: `almacen → instalacion → instalado → desinstalacion →
  almacen`, o `(instalado|almacen) → envio_reparacion/envio_reencauche → reparacion →
  retorno_taller → almacen`. `apply_movement` rechaza transiciones fuera de ese grafo.
- "Reemplazo definitivo" (retiro de un neumático) no está modelado como estado aparte — el enum de
  `status` se mantiene en los 3 valores acordados (instalado/almacen/reparacion). La analítica de
  rendimiento por ahora solo reporta km hasta envío a reparación/reencauche; si una fase futura
  necesita medir reemplazo definitivo, requiere agregar un 4º estado (decisión pendiente, no tomada
  unilateralmente en esta fase).
