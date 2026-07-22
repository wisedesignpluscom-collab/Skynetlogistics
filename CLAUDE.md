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
- **Fase 6 (Inventario/repuestos): completa.** Backend probado (165 tests en total, 21 nuevos de
  esta fase) y frontend verificado end-to-end en navegador (alta de ítems de inventario con stock
  inicial en cero, entrada/salida/ajuste de stock vía bitácora de movimientos, badge de stock bajo
  en el listado con filtro dedicado, alerta automática al caer a o bajo el mínimo configurado,
  rechazo de salidas que dejarían el stock negativo). `Inventario` reemplaza el placeholder de
  "Próximamente" en el sidebar.
- **Fase 7A (Optimizador de rutas — ruteo punto a punto): completa.** Backend probado (191 tests en
  total, 26 nuevos de esta fase, incluida la geometría de desvío verificada contra valores calculados
  a mano) y frontend verificado end-to-end en navegador (ruta planeada sobre mapa Leaflet, posición
  real del vehículo superpuesta, cálculo bajo demanda con coords, recálculo manual, y — vía una
  posición GPS simulada por webhook — recálculo automático por desvío con banner de notificación e
  historial, más alerta `route_deviation` en el panel). El motor de ruteo activo en dev/tests es
  `fake` (determinista, sin red); Mapbox Directions queda detrás del mismo adapter para producción.
- **Fase 7B (Optimización multi-parada / VRP con OR-Tools): completa.** Backend probado (231 tests
  en total, 40 nuevos de esta fase, incluida la matriz de distancias y el solver verificados con
  coordenadas fijas) y frontend verificado end-to-end en navegador (captura de paradas, selector de
  vehículos candidatos con default "todos los disponibles", propuesta del solver en mapa Leaflet
  multi-vehículo con distancia/duración estimadas por vehículo, confirmación que crea un trip por
  vehículo con su ruta real ya calculada, descarte de una propuesta). Alcance acordado: VRP
  multi-vehículo sin restricciones de capacidad ni ventanas de tiempo, rutas abiertas (sin retorno
  al punto de partida), paradas capturadas manualmente antes de optimizar (no a partir de trips ya
  creados). `VrpOptimizationPage` no tiene entrada propia en el `Sidebar` — se llega vía un botón
  "Optimizar rutas (VRP)" en `TripsPage`, mismo patrón que `trip-settings`.
- **Fase 8 (Reportes de conductor en tiempo real + chat interno): completa.** Backend probado
  (243 tests en total, 12 nuevos de esta fase — reportes de incidencia con aislamiento "solo lo
  propio", alerta automática de severidad alta/crítica, y chat conductor↔despachador) y frontend
  verificado end-to-end en navegador (login del conductor → portal móvil-first → reporte de
  accidente crítico → alerta generada en el panel del despachador → chat en vivo bidireccional por
  WebSocket sin recargar → despachador resuelve el reporte con notas). Alcance:
  el conductor entra con login propio (`drivers.user_id` → rol "Conductor" con permisos acotados) a
  un portal móvil-first separado (`DriverPortalLayout`, sin `Sidebar`) donde reporta incidencias
  (10 tipos + "otro": accidente/siniestro/avería/falta de viáticos/multa/retraso/pernocte/mercancía
  dañada/retención en aduana/emergencia de salud) y chatea; el despachador ve todo en `IncidentsPage`
  (badge "Reportes" en el `Sidebar`, gateado por permiso `incidents`) y responde el chat en vivo vía
  WebSocket. **Esta fase renumera el plan original: lo que era Fase 8 (Reportes/BI) pasa a Fase 9, y
  Fase 9 (módulos auxiliares) a Fase 10.**
- **Fase 9 (Reparto/delivery + CVRP): en progreso, spec aprobado.** Alcance acordado: catálogo de
  mercancía de reparto con control de stock, pedidos de reparto enlazados al optimizador VRP, CVRP
  con capacidad por vehículo, y confirmación de entrega por conductor + despachador. Se desarrolla en
  3 sub-fases (9A/9B/9C), revisando cada una antes de la siguiente.
  - **9A (catálogo de mercancía de reparto + stock): completa.** Backend probado (250 tests en total,
    7 nuevos) y frontend verificado end-to-end en navegador (alta de mercancía con peso/volumen por
    unidad, entrada de stock vía bitácora de movimientos, badge de stock bajo, alerta automática
    `low_stock_delivery`). `delivery_goods`/`delivery_goods_movements` reutilizan EXACTAMENTE el
    patrón de Inventario (Fase 6): `apply_movement` atómico, stock derivado (solo vía movimientos), y
    `run_alert_checks` extendido con `goods_ids` (sin reimplementar deduplicación). Módulo nuevo
    `delivery` (permiso propio), entrada "Reparto" en el `Sidebar`. El peso/volumen por unidad se
    captura ya en 9A porque alimentará la demanda de cada parada en el CVRP de 9C.
  - **9B (pedidos de reparto + confirmación de entrega): completa.** Backend probado (7 nuevos
    tests) y frontend verificado end-to-end en navegador (despachador crea pedido con líneas de
    mercancía → asigna a un viaje del conductor, lo que DESCUENTA stock automáticamente → el
    conductor ve la entrega en su portal móvil de Fase 8 y la marca "entregado"). `delivery_orders`
    (FK a `clients`/`trips`) + `delivery_order_items` (FK a `delivery_goods`). Ciclo:
    `pendiente → asignado → en_ruta → entregado/fallido`. `services/delivery_dispatch.py` centraliza
    las transiciones y el efecto sobre el stock: `assign_to_trip` valida stock de TODAS las líneas
    antes de descontar cualquiera y descuenta vía `delivery_goods_movements.apply_movement` (9A);
    `mark_failed(return_stock=True)` reingresa la mercancía. **Este servicio lo reutilizará el
    confirm del VRP en 9C** (mismo criterio "un único punto de entrada" que `vrp_planning`). La
    entrega/fallo la pueden marcar TANTO el despachador (permiso `delivery`) COMO el conductor
    (`get_current_driver` + validación de que el pedido está en uno de sus trips activos) — el actor
    se resuelve dentro del endpoint, mismo patrón que el chat de Fase 8. El `Sidebar` "Reparto" ahora
    apunta a `DeliveryOrdersPage` (pedidos); el catálogo de mercancía (9A) queda como botón
    secundario. El conductor accede a "Mis entregas" desde su portal.
  - **9C (enlace CVRP: capacidad en vehicles, solver con dimensión de capacidad, optimizar desde
    pedidos, descuento de stock al despachar): completa.** Backend probado (15 nuevos tests — solver
    con capacidad verificado con coords fijas, optimizar desde pedidos, despacho que descuenta stock,
    infactibilidad por exceso de carga) y frontend verificado end-to-end en navegador (modo "desde
    pedidos pendientes" en `VrpOptimizationPage` → propuesta con carga vs capacidad por vehículo
    (74/200 kg, 0.48/5 m³) → confirmar crea el trip, despacha ambos pedidos al mismo trip y descuenta
    stock 20→16). Piezas: `vehicles.cargo_capacity_kg` (ya existía) + `cargo_capacity_m3` (nuevo);
    `solve_vrp` gana `capacity_dims: list[CapacityDimension]` opcional → `AddDimensionWithVehicleCapacity`
    de OR-Tools por magnitud (peso/volumen), escalando kg/m³ a enteros (×1000); sin dims el solver es
    idéntico al mTSP de 7B (retrocompat verificada). `VrpOptimizeRequest` acepta `stops` (manual, 7B)
    O `order_ids` (pedidos, 9C) — exactamente uno, validado con `model_validator`. `propose_optimization`
    deriva paradas + demanda peso/volumen de cada pedido (suma de líneas × `delivery_goods`), incluye
    una dimensión de capacidad solo si algún vehículo del pool la declara (a los sin-límite se les da
    un tope "ilimitado"); `enforce_capacity=False` la desactiva. `confirm_run` reutiliza
    `delivery_dispatch.assign_to_trip` (9B) para despachar cada pedido de la ruta a su trip — único
    punto de entrada al stock, sin tocarlo aquí. Las paradas del VRP llevan `order_id` opcional (vacío
    en modo manual) para saber qué pedido despachar al confirmar.
- **Renumeración de fases confirmada:** la antigua Fase 8 (Reportes/BI) es ahora Fase 10, y la
  antigua Fase 9 (auxiliares) la Fase 11 (ver tabla de fases más abajo, aún sin actualizar en detalle).
- **Configuración sin código: completa (Config-A/B/C).** Módulo para que los admins adapten el
  sistema a su nicho sin tocar código — campos custom, reglas de formulario/validación y workflows
  condición→acción, aplicados a las 9 entidades principales del sistema.
  - **Config-A (campos custom + opciones de listas): completa.** Backend probado (262 tests en total,
    12 nuevos) y frontend verificado end-to-end en navegador (admin crea un campo `select`
    obligatorio "Categoría interna" para Vehículos → aparece automáticamente en el formulario de
    vehículo → se crea el vehículo con `custom_data={"categoria_interna":"interurbano"}`; validación
    de obligatorio y de opción inválida devuelven 422). Piezas: `custom_field_definitions`
    (`company_id, entity_type, key, label, field_type, options JSONB, required, order, active`) +
    una columna `custom_data` JSONB en las 9 entidades habilitadas (vehicle/driver/trip/
    delivery_order/client/maintenance_task/inventory_item/tire/delivery_goods). El validador puro
    `services/custom_fields.py::validate_custom_data(definitions, data)` (tipos, required, select
    dentro de opciones; descarta keys desconocidas) lo envuelve `validate_entity_custom_data` (→422)
    que cada endpoint de entidad llama en create/update. Permiso nuevo `config` para administrar
    (crear/editar/borrar definiciones); LISTARLAS no exige `config` (cualquiera que edita una entidad
    necesita conocer sus campos para renderizarlos). Frontend: `ConfigPage` (entrada "Configuración"
    en el `Sidebar`, gateada por `config`) administra los campos por entidad; el componente genérico
    `components/config/CustomFieldsSection.tsx` renderiza los campos activos y se inserta en el
    formulario de cada entidad editando `custom_data` (integrado por ahora en `VehicleFormModal`;
    insertarlo en los demás formularios es el mismo patrón de una línea). **Fuera de alcance de A**
    (decisión pendiente): extender los *enums de sistema* con `CheckConstraint` (tipo de vehículo,
    estados…) por empresa — requiere quitar esos constraints y validar en app; con campos custom
    tipo `select` se cubre el caso de nicho sin ese riesgo.
  - **Config-B (reglas de formulario + reglas de validación): completa.** Backend probado (18 tests
    nuevos: evaluador de condiciones, evaluador de fórmulas, endpoints, reglas de validación en las
    9 entidades) y frontend verificado end-to-end en navegador (regla de formulario "ocultar campo
    custom si tipo=remolque" se aplica en vivo al cambiar el select, sin recargar; regla de
    validación "año < 2015 → bloquear" devuelve 422 con el mensaje configurado, año válido crea
    normal). Piezas: `form_rules` (`company_id, entity_type, name, kind` formulario|validacion,
    `condition` JSONB, `actions` JSONB, `active`, `order`). Evaluador de condiciones puro
    (`services/form_rules.py::evaluate_condition`, gemelo TS en `features/config/ruleEngine.ts` —
    misma semántica, ops igual/distinto/mayor/menor/≥/≤/en_lista/contiene/vacío/no_vacío) y
    evaluador de fórmulas puro sin `eval` (parser aritmético propio) para la acción `calcular`. El
    catálogo de campos por entidad (`GET /custom-fields/entity-schema?entity_type=`) combina campos
    de sistema "reglables" (definidos a mano por entidad) con los custom de Config-A
    (`custom.<key>`), y alimenta tanto el editor de reglas como el evaluador.
    **Extensión: reglas de formulario también controlan campos de sistema.** Cada uno de los 9
    formularios llama `features/config/useSystemFieldRules.ts` (arma el contexto — campos de
    sistema + custom aplanados como `custom.<key>` — y evalúa las reglas activas una sola vez) y
    envuelve sus inputs "reglables" (los mismos declarados en `services/entity_fields.py`) con
    `rules.isHidden`/`rules.isRequired`, aplicando `rules.computed` vía un mapa de setters por
    campo. Ese mismo objeto `rules` se pasa a `CustomFieldsSection` (prop `rules`, opcional — si no
    se pasa, sigue evaluando por su cuenta) para no recargar/reevaluar las reglas dos veces.
    Verificado en navegador: una regla "ocultar Marca si tipo=remolque" (campo de sistema) y una
    regla previa "ocultar Categoría interna si tipo=remolque" (campo custom) conviven y se aplican
    en vivo simultáneamente sin conflicto. Frontend: pestañas "Campos personalizados"/"Reglas" en
    `ConfigPage`; editor de reglas (`RuleFormModal`) con constructor de condición+acciones sin
    código.
  - **Config-C (workflows condición→acción): completa.** Backend probado (9 tests nuevos: creación/
    validación de acciones, disparo de `crear_alerta` y `actualizar_campo` al cumplirse la condición,
    no-disparo cuando la condición no aplica o el workflow está inactivo, `cambio_estado` verificado
    con el valor anterior, aislamiento por permiso `config`) y frontend verificado end-to-end en
    navegador (workflow "crear alerta si tipo=remolque" al crear un vehículo → la alerta aparece
    automáticamente en el panel del despachador, sin intervención manual). A diferencia de Config-B
    (que actúa mientras se llena el formulario o bloquea antes de guardar), los workflows corren
    **después** de persistir, como efecto secundario best-effort — mismo criterio que el auto-trigger
    de ruteo de Fase 7A. `workflows` (`company_id, entity_type, name, event` creado|actualizado|
    cambio_estado, `condition` JSONB, `actions` JSONB, `active`, `order`) reutiliza el evaluador puro
    de condiciones de Config-B (`services/rule_engine.py`) y el catálogo de campos por entidad
    (`services/entity_fields.py`) — sin reimplementar ninguno de los dos. `services/workflows.py::
    run_workflows(db, company_id, entity_type, event, entity, previous_status=None)` arma el contexto
    desde el registro YA persistido (no desde el payload) y ejecuta las acciones de los workflows que
    matchean; nunca lanza — un workflow roto se loguea y no afecta la respuesta del endpoint que ya
    completó su guardado. Dos acciones en esta primera versión: `crear_alerta` (reutiliza
    `create_if_not_exists` de Fase 1, dedupe por `type=workflow_<id>`) y `actualizar_campo` (solo
    campos **custom**, `target` debe empezar con `custom.`, validado en el schema). Integrado en las
    9 entidades: `creado`/`actualizado` siempre tras el commit del endpoint; `cambio_estado` solo en
    las 3 entidades cuyo `status` es parte del payload del PATCH genérico
    (`STATUS_UPDATABLE_ENTITIES` en `workflows.py`: vehicle/driver/maintenance_task, este último
    también en `/complete`) — trip/delivery_order/tire cambian de estado vía endpoints de transición
    especializados (start/close, assign/deliver, movements) no cubiertos por `cambio_estado` en esta
    versión, decisión de alcance explícita, no un olvido. El campo sintético `previous_status` queda
    disponible como condición solo cuando `event=cambio_estado` (se arma en el frontend, no viene del
    catálogo del backend). Frontend: tercera pestaña "Workflows" en `ConfigPage`, mismo editor visual
    de condición que Config-B más un bloque de acciones específico (mensaje+severidad para
    `crear_alerta`, campo custom+valor para `actualizar_campo`).
- La antigua **Fase 10 (Reportes/BI + exportaciones)** sigue pendiente.

### Notas de diseño de Fase 8 (reportes de conductor + chat)

- **Conductor con login (`drivers.user_id`, FK unique nullable a `users`):** un conductor solo puede
  loguearse si tiene `user_id`. El aislamiento "solo lo propio" NO se resolvió extendiendo
  `require_permission` (que es por módulo, no por fila) sino con la dependency
  `app/core/deps.py::get_current_driver`, que deriva el `Driver` desde el token — los endpoints
  driver-facing (`POST /incident-reports`, `/chat/my-thread`, subida de adjuntos) nunca aceptan
  `driver_id` del cliente. El rol "Conductor" no es de sistema sembrado: el admin lo crea por empresa
  vía `/roles` con `DRIVER_SUGGESTED_PERMISSIONS` (`incidents`/`chat` write, `trips` read).
- **Alerta de incidencia no es un job del barrido:** a diferencia del resto de chequeos de
  `app/jobs/alerts.py`, `create_incident_alert` se llama directo desde `POST /incident-reports` al
  crear un reporte de severidad alta/crítica, reutilizando `create_if_not_exists` (Fase 1). El enum
  de `alerts.severity` solo tiene 3 niveles y el de incidencias 4 — "critica" cae en "alta" vía
  `INCIDENT_SEVERITY_TO_ALERT_SEVERITY`, mismo desajuste ya documentado para fatiga.
- **Tiempo real vía WebSocket in-process (`app/core/websocket_manager.py`):** un `ConnectionManager`
  en memoria, un solo proceso, mismo criterio que el `AsyncIOScheduler` (sin Redis/pubsub hasta que
  haya múltiples instancias del backend). Canales `/ws/company` (despachador) y `/ws/driver`
  (conductor), autenticados por query param porque el handshake WebSocket del navegador no permite
  headers custom. Al crear un reporte o mensaje se hace broadcast a los conectados relevantes.
- **Adjuntos en filesystem local (`app/core/file_storage.py`):** se guardan bajo
  `uploads/<company_id>/incidents/<incident_id>/` y se sirven vía `StaticFiles` en `/uploads`
  (límite 10 MB, solo jpeg/png/webp/pdf). Migrar a un bucket S3-compatible más adelante es un cambio
  acotado a ese archivo, sin tocar endpoints — mismo criterio adapter que GPS/routing.
- **Chat: un hilo por (driver_id, incident_report_id):** si `incident_report_id` es NULL es el chat
  general de dudas del conductor (uno solo, reutilizado vía `get_or_create_thread`); si no, el hilo
  atado a ese reporte. No hay tabla de "participantes": el `sender_type` (conductor/despachador) se
  infiere de si el usuario logueado tiene un `Driver` vinculado.
- **Frontend con layout separado:** el portal del conductor (`/driver`, `/driver/chat`,
  `/driver/incidents/:id`) usa `DriverPortalLayout` (móvil-first, sin `Sidebar`), no
  `DashboardLayout`. El `ProtectedRoute` de gestión redirige a `/driver` si el usuario es conductor,
  y `DriverProtectedRoute` hace lo inverso. `useLiveSocket` (WebSocket con reconexión por backoff)
  refresca el chat/listado en vivo — sin librería nueva. El login (`LoginPage`) redirige según
  `driver_id` que ahora devuelven `/auth/login` y `/auth/me`.

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
- **Motor de ruteo:** Mapbox Directions API en 7A (detrás de un adapter `RoutingEngine`, `fake` en
  tests); OSRM self-hosted queda como motor alternativo futuro sin cambios de código
- **Optimización VRP:** Google OR-Tools (`ortools`, Fase 7B)
- **Colas/jobs:** para ingesta GPS y cálculo de alertas (ej. Celery + Redis, o APScheduler si el volumen es bajo al inicio)

## Reglas de trabajo con Claude Code

1. No escribir código sin aprobación explícita del spec de cada fase.
2. Cada fase se desarrolla, se revisa, se aprueba, y se hace `/clear` antes de iniciar la siguiente.
3. Reutilizar patrones y componentes ya definidos en fases anteriores (no reinventar).
4. Toda tabla nueva debe declarar sus relaciones (FK) explícitamente antes de generar migraciones.
5. Estética (rediseño 2026): **light-mode SaaS**, tipografía sans-serif (Inter), acento **azul**
   (`#2d5bff`), sidebar vertical **azul royal** (`#2946d8`) con iconos, header blanco con breadcrumb
   "Principal / …" y avatar de iniciales, cards blancas con borde/sombra suave sobre fondo lavanda
   claro (`#eef1f9`). Reemplaza la identidad anterior (dark-mode + oro/cobre + serif de Wise
   Designs+). Los tokens de `@theme` conservan sus nombres antiguos (p.ej. `gold` = primario azul,
   `font-display` = Inter) para no reescribir cada pantalla — ver la nota de Tailwind v4 abajo.

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
- **`app/services/inventory_movements.py::apply_movement`** centraliza la transición de stock de un
  ítem (`entrada`/`salida`/`ajuste`): calcula el delta según el tipo (`entrada`/`salida` siempre con
  cantidad positiva, `ajuste` con delta con signo explícito), valida que `quantity` nunca quede
  negativa, actualiza `inventory_items` y crea el `inventory_movement` de forma atómica — mismo
  patrón que `tire_movements.py::apply_movement` (Fase 5). `quantity` en `inventory_items` es un
  campo derivado: `InventoryItemUpdate` (PATCH) no lo acepta, solo se modifica vía movimientos.
- **Alerta de stock bajo no es un job nuevo:** extiende `run_alert_checks` (`app/jobs/alerts.py`) con
  un parámetro `item_ids` independiente de `vehicle_ids` (ambos scoping opcionales, mutuamente
  excluyentes en la práctica) — genera alerta `low_stock` (`entity_type="inventory_item"`) cuando
  `quantity <= min_stock`, reutilizando `create_if_not_exists` (Fase 1) para el anti-duplicado. Se
  dispara scoped al ítem tras cada movimiento, y también en el barrido diario completo.
- **Validación de `warehouse_id`/`vehicle_id` cross-tenant en `inventory_items`/`inventory_movements`:**
  a diferencia del `warehouse_id` opcional de `tires` (Fase 5, sin validar contra `company_id`), aquí
  sí se valida explícitamente (`warehouse_crud.get`/`vehicle_crud.get` con `company_id`) antes de
  crear/actualizar, devolviendo 404 si el recurso referenciado es de otra empresa — cierra un hueco
  de aislamiento multiempresa que Fase 5 había dejado abierto; aplicar el mismo criterio a cualquier
  FK cross-tabla nueva en fases futuras.
- **Motores de ruteo (`app/routing_engines/`, Fase 7):** mismo patrón que `gps_adapters/` — interfaz
  `RoutingEngine.route()` + `ENGINE_REGISTRY`, motor activo elegido por `settings.routing_engine`.
  `FakeRoutingEngine` (determinista, interpola una recta y estima con haversine) es el default en
  dev/tests para no tocar la red; `MapboxRoutingEngine` (Directions API, token en
  `settings.mapbox_access_token`) es el de producción. Migrar a OSRM self-hosted en el futuro es un
  motor nuevo en el registry + cambio de config, sin tocar servicios ni endpoints. Los tests son
  herméticos porque corren sobre `fake`.
- **Geometría de desvío (`app/services/route_geometry.py`):** función pura (sin red/DB) que calcula
  la distancia mínima punto-a-polyline en metros vía proyección equirectangular local (escala lng por
  `cos(lat)`), testeable con coords fijas contra valores a mano — mismo criterio que las fórmulas de
  nómina/fatiga. La geometría se maneja siempre como `[[lng, lat], ...]` (orden GeoJSON) en
  `route_plans.geometry`; el frontend la invierte a `[lat, lng]` para Leaflet.
- **Planificación de rutas (`app/services/route_planning.py`):** único punto que invoca el motor y
  escribe geometría — lo comparten el auto-trigger al crear viaje, el cálculo bajo demanda, el
  recálculo manual y el automático por desvío. `compute_route_plan` NUNCA toca `trips.distance_km`
  (dato operativo del flete, Fase 2); la distancia estimada vive solo en
  `route_plans.calculated_distance_km`. `check_deviation_and_recalculate` (llamada best-effort desde
  el webhook GPS) busca el viaje `en_curso` del vehículo, mide el desvío contra la polyline, respeta
  `route_settings.deviation_threshold_m` (default 150 m) y `recalc_cooldown_min` (default 5 min),
  recalcula, registra `route_recalculations(reason='desvio')` y genera alerta `route_deviation`
  reutilizando `create_if_not_exists` (Fase 1) — sin lógica nueva de deduplicación.
- **Auto-trigger de ruteo en `POST /trips`:** `TripCreate` acepta 4 coords opcionales; si vienen las
  cuatro, tras crear el viaje se calcula el `route_plan` (best-effort, no bloquea la creación si el
  motor falla). `trip_crud.create` excluye las coords del `model_dump` porque no son columnas de
  `trips`. `route_settings` sigue el patrón get-or-create por empresa (como `fatigue_rules`), y todo
  el módulo de ruteo se gatea con el permiso `trips` existente (no se creó un módulo nuevo).
- **VRP multi-vehículo (`app/services/vrp_optimization.py`, `vrp_distance_matrix.py`,
  `vrp_planning.py`, Fase 7B):** el solver (`solve_vrp`, OR-Tools `pywrapcp`) es una función pura
  que recibe una matriz de distancias haversine (`build_distance_matrix_m` — sin red, testeable con
  coords fijas, mismo criterio que `route_geometry.py`) y resuelve un mTSP sin capacidad ni
  ventanas de tiempo. Rutas abiertas (cada vehículo no vuelve a su punto de partida) vía el truco
  estándar de OR-Tools: el nodo de partida de cada vehículo también actúa como su nodo de "regreso",
  pero todo arco hacia ese nodo cuesta 0 — el solver nunca paga (ni optimiza) el tramo de vuelta.
  `vrp_planning.propose_optimization` arma el pool de vehículos candidatos (activos, con conductor
  asignado, sin viaje `en_curso`, con posición GPS conocida — es su punto de partida) y guarda la
  propuesta en un `VrpRun` (`status='propuesto'`) sin crear trips todavía; la distancia/duración de
  la propuesta se estima con haversine (`estimate_route_km_and_min`), no con el motor de ruteo real.
  `confirm_run` recién ahí crea un trip por vehículo (`is_round_trip=False`, `distance_km=None` —
  igual que 7A, nunca se toca el dato operativo del flete) y llama
  `route_planning.compute_multi_stop_route_plan` para la geometría real.
- **Ruta real a través de paradas sin tocar `RoutingEngine`:** en vez de extender la interfaz de
  7A con soporte nativo de waypoints, `compute_multi_stop_route_plan` llama al motor activo una vez
  por tramo (origen→parada1→parada2→...→última parada, mismo `engine.route()` de 7A) y concatena
  geometría/distancia/duración — mismo "único punto de entrada al motor", sin cambiar el contrato
  que ya usa Mapbox/fake. `route_plan_crud.upsert_for_trip` ahora acepta `waypoints` opcional (7A no
  lo pasa y queda `[]`; 7B lo llena con las paradas ordenadas — el campo que quedó reservado desde
  el modelo de `route_plans` en 7A).
- **`vrp_runs`** es la bitácora de auditoría de cada corrida (`input_stops`, `vehicle_ids_considered`,
  `proposed_assignment`, `status` propuesto/confirmado/descartado, `result_trip_ids`), mismo criterio
  que `route_recalculations` (7A). No hay tabla de "paradas" aparte: las paradas confirmadas viven
  únicamente en `route_plans.waypoints` del trip resultante, sin duplicar el dato.
- **Límite duro de 60 paradas por corrida** (`vrp_planning.MAX_STOPS_PER_RUN`, validado también en
  el schema `VrpOptimizeRequest`) para mantener el solve síncrono dentro de un timeout de request
  razonable — no se plantea como job en background.

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
- **Tailwind v4:** tema definido vía `@theme` en `src/styles/index.css`, no en `tailwind.config.*`
  (patrón nativo de Tailwind v4). **Rediseño 2026 (light-mode azul):** se cambiaron SOLO los valores
  de los tokens en `@theme`, conservando sus nombres — `--color-gold` es ahora el primario azul
  (`#2d5bff`), `--color-background` el lavanda claro, `--color-surface` blanco, `--font-display`
  pasa a Inter, y se añadieron `--color-sidebar*`. Como casi todas las pantallas usan clases
  semánticas (`bg-surface`, `text-gold`, `border-border`, `font-display`…), el cambio de paleta se
  propagó sin tocarlas; solo se reescribieron a mano `Sidebar` (azul con iconos SVG inline),
  `DashboardLayout` (header + breadcrumb + avatar de iniciales) y los primitivos `Button/Modal/Badge`.
  Para un acento azul nuevo, reutilizar el token `gold` (no introducir un color hardcodeado).
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
- **`InventoryPage` reutiliza `useWarehouses`/`Warehouse` de `features/tires`** en vez de duplicar el
  fetch de almacenes — el botón "Almacenes" de `InventoryPage` reusa `WarehousesPage` (Fase 5) tal
  cual, sin cambios, y por eso queda gateado por el permiso `tires` (no `inventory`) igual que en el
  backend. `Inventario` sí tiene entrada directa en el `Sidebar` (reemplaza el placeholder de
  "Próximamente"); el detalle de ítem (`/inventory/:itemId`, con historial de movimientos) se llega
  haciendo click en el SKU en `InventoryTable`, mismo patrón que `TireTable`/`DriverTable`.
- **Ruta planeada (Fase 7) sin ruta propia en el `Sidebar`:** `TripRoutePage` (`/trips/:tripId/route`)
  se llega vía un link "Ruta planeada" dentro de `TripDetailPage`, igual que "Ver ruta GPS" (Fase 3).
  Reutiliza el mismo mapa Leaflet + tiles oscuros de CARTO de Fase 3: dibuja la polyline planeada
  (dorada) más la última posición real del vehículo (`CircleMarker` azul, vía `getLatestPosition` de
  Fase 3), un banner rojo cuando el último recálculo fue por desvío, y el historial de recálculos. El
  `TripFormModal` incluye un `<details>` opcional con las 4 coords para disparar el cálculo de ruta al
  crear el viaje. Sin librería de mapas nueva — Leaflet sigue siendo la única externa del proyecto.
- **`VrpOptimizationPage` (Fase 7B) sin ruta propia en el `Sidebar`:** se llega vía el botón
  "Optimizar rutas (VRP)" en `TripsPage`, mismo patrón que `trip-settings`. Flujo de una sola
  pantalla con estado local (sin persistir el borrador): captura de paradas (lat/lng/etiqueta) +
  selector de vehículos candidatos (`useAvailableVehicles`, precargado con todos los disponibles) →
  `POST /vrp/optimize` → la propuesta se dibuja en `VrpProposalMap` (mismo mapa Leaflet + tiles CARTO
  de Fase 3/7A, una polyline de color distinto por vehículo, posición GPS de partida vía
  `getLatestPosition` de Fase 3) con una tabla de paradas/distancia/duración estimada por vehículo →
  "Confirmar y crear viajes" o "Descartar". Tras confirmar, enlaces directos a cada trip creado
  (`/trips/:tripId`) y a su ruta real ya calculada (`/trips/:tripId/route`, reutiliza `TripRoutePage`
  de 7A sin cambios). Sin librería de mapas ni de optimización nueva en el frontend — el solver corre
  enteramente en el backend.

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
  Inventario más abajo); Fase 6 la reutiliza tal cual, sin agregarle campos

### Inventario
- **warehouses** — ver Neumáticos (Fase 5); Fase 6 no le agregó campos, se reutiliza tal cual
- **inventory_items** — id, company_id, warehouse_id, sku (único por empresa), name, unit,
  quantity (derivado, solo vía movimientos), min_stock, unit_cost
- **inventory_movements** — id, company_id, item_id, vehicle_id (nullable), movement_type
  (entrada/salida/ajuste), quantity, unit_cost (nullable, snapshot en entrada), reference_doc
  (nullable), notes, recorded_by, created_at

### GPS / Telemetría (hypertable — TimescaleDB)
- **gps_providers** — id, company_id, provider_name, api_credentials (encriptado), adapter_type
- **vehicle_positions** (hypertable) — vehicle_id, timestamp, lat, lng, speed_kmh, odometer_km, ignition_status, heading
- **gps_provider_vehicle_map** — vehicle_id, provider_id, external_device_id

### Optimización de rutas
- **route_plans** — id, company_id, trip_id (unique — un plan vigente por viaje),
  origin_lat/origin_lng, destination_lat/destination_lng (Numeric(9,6), en vez de un `*_coords`
  opaco), geometry (JSONB, GeoJSON LineString `[[lng,lat],...]` — agregada respecto al sketch
  original: necesaria para dibujar la ruta y medir el desvío), waypoints (JSONB, vacío en 7A; 7B lo
  llena), calculated_distance_km, calculated_duration_min, engine_used
- **route_recalculations** — id, company_id, route_plan_id (FK CASCADE), reason
  (desvio/manual/trafico), deviation_m (nullable), trigger_lat/trigger_lng (nullable),
  new_distance_km, new_duration_min, new_route_data (JSONB), created_at
- **route_settings** — id, company_id (unique), deviation_threshold_m (default 150),
  recalc_cooldown_min (default 5) — umbral/cooldown configurables por empresa, mismo patrón que
  `fatigue_rules` (Fase 4) / `tire_settings` (Fase 5)
- **vrp_runs** (Fase 7B) — id, company_id, input_stops (JSONB), cargo_type, vehicle_ids_considered
  (JSONB), proposed_assignment (JSONB), status (propuesto/confirmado/descartado), result_trip_ids
  (JSONB), created_by, created_at — bitácora de auditoría de cada corrida del solver; sin tabla de
  "paradas" aparte, las paradas confirmadas viven en `route_plans.waypoints` del trip resultante

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
