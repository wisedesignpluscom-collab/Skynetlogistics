MODULES = (
    "companies",
    "users",
    "roles",
    "vehicles",
    "drivers",
    "providers",
    "maintenance",
    "alerts",
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
}


def has_permission(permissions: dict[str, list[str]], module: str, action: str) -> bool:
    return action in permissions.get(module, [])
