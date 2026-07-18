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
- Próxima fase en curso: **Fase 1 (Mantenimiento + Alertas)** — en etapa de propuesta de
  esquema/endpoints, pendiente de aprobación antes de generar código (ver regla 1).

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
  `roles.permissions` (JSONB `{modulo: [acciones]}`), ver `app/utils/permissions.py`.
- **Auth:** access token JWT de corta vida (`app/core/security.py`); refresh token opaco
  (`secrets.token_urlsafe`) cuyo hash SHA-256 se guarda en `refresh_tokens` — rota en cada uso
  (`/auth/refresh` revoca el anterior y emite uno nuevo). Password con bcrypt.
- **`Base.__mapper_args__ = {"eager_defaults": True}`** (`app/core/database.py`) es necesario en
  todo modelo nuevo con columnas `server_default`/`onupdate`: sin esto, leer esas columnas tras un
  flush en modo async revienta con `MissingGreenlet`.
- **Seed:** `app/seed.py` crea la empresa "Platform", el rol de sistema "Superadmin" y el primer
  usuario superadmin — es el único punto de entrada para crear el primer usuario del sistema.

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
- **tires** — id, unique_code, brand, model, current_thickness_mm, status (instalado/almacén/reparación)
- **tire_movements** — id, tire_id, vehicle_id (nullable), axle_position, warehouse_id (nullable), km_at_movement, movement_type, timestamp

### Inventario
- **warehouses** — id, company_id, name, location
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
