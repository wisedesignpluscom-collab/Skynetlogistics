MODULES = (
    "companies",
    "users",
    "roles",
    "vehicles",
    "drivers",
    "providers",
    "maintenance",
    "alerts",
    "trips",
    "trip_settings",
    "gps",
    "fatigue",
    "tires",
    "inventory",
    "incidents",
    "chat",
    "delivery",
    "config",
)
ACTIONS = ("read", "write", "delete")

# Rol sembrado por defecto para el primer administrador de cada empresa nueva.
DEFAULT_ADMIN_PERMISSIONS: dict[str, list[str]] = {
    "users": ["read", "write", "delete"],
    "roles": ["read", "write", "delete"],
    "vehicles": ["read", "write", "delete"],
    "drivers": ["read", "write", "delete"],
    "providers": ["read", "write", "delete"],
    "maintenance": ["read", "write", "delete"],
    "alerts": ["read", "write"],
    "trips": ["read", "write", "delete"],
    "trip_settings": ["read", "write", "delete"],
    "gps": ["read", "write", "delete"],
    "fatigue": ["read", "write"],
    "tires": ["read", "write", "delete"],
    "inventory": ["read", "write", "delete"],
    "incidents": ["read", "write", "delete"],
    "chat": ["read", "write"],
    "delivery": ["read", "write", "delete"],
    "config": ["read", "write", "delete"],
}

# Permisos sugeridos para un rol "Conductor": el admin de cada empresa crea este rol vía
# `/roles` (no es un rol de sistema sembrado, mismo criterio que el resto de roles por empresa) y
# le asigna estos permisos. El aislamiento "solo lo propio" no lo resuelve el módulo de permisos
# (que es por módulo, no por fila) sino los endpoints driver-facing en incident_reports.py/chat.py,
# que siempre derivan driver_id desde `get_current_driver` en vez de aceptarlo del cliente.
DRIVER_SUGGESTED_PERMISSIONS: dict[str, list[str]] = {
    "incidents": ["read", "write"],
    "chat": ["read", "write"],
    "trips": ["read"],
}

# Permisos del rol de sistema "Superadmin" (plataforma, cross-tenant).
SUPERADMIN_PERMISSIONS: dict[str, list[str]] = {
    "companies": ["read", "write", "delete"],
    "users": ["read", "write", "delete"],
    "roles": ["read", "write", "delete"],
    "vehicles": ["read", "write", "delete"],
    "drivers": ["read", "write", "delete"],
    "providers": ["read", "write", "delete"],
    "maintenance": ["read", "write", "delete"],
    "alerts": ["read", "write"],
    "trips": ["read", "write", "delete"],
    "trip_settings": ["read", "write", "delete"],
    "gps": ["read", "write", "delete"],
    "fatigue": ["read", "write"],
    "tires": ["read", "write", "delete"],
    "inventory": ["read", "write", "delete"],
    "incidents": ["read", "write", "delete"],
    "chat": ["read", "write"],
    "delivery": ["read", "write", "delete"],
    "config": ["read", "write", "delete"],
}


def has_permission(permissions: dict[str, list[str]], module: str, action: str) -> bool:
    return action in permissions.get(module, [])
