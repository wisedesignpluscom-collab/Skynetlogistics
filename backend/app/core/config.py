from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"

    database_url: str = "postgresql+asyncpg://fleet:fleet_dev_pw@localhost:5432/fleet_db"

    @field_validator("database_url")
    @classmethod
    def _use_asyncpg_driver(cls, value: str) -> str:
        # Hosts como Render/Railway/Heroku entregan DATABASE_URL como
        # postgres:// o postgresql://; el driver async necesita +asyncpg.
        if value.startswith("postgres://"):
            value = "postgresql+asyncpg://" + value[len("postgres://") :]
        elif value.startswith("postgresql://"):
            value = "postgresql+asyncpg://" + value[len("postgresql://") :]

        # Proveedores como Neon/Supabase entregan `sslmode=require` en la query
        # string (convención de psycopg2); asyncpg no reconoce ese kwarg y
        # revienta con TypeError al conectar. asyncpg sí acepta el mismo valor
        # bajo la key `ssl`.
        parts = urlsplit(value)
        query = dict(parse_qsl(parts.query))
        if "sslmode" in query:
            query["ssl"] = query.pop("sslmode")
            value = urlunsplit(parts._replace(query=urlencode(query)))

        return value

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"

    seed_superadmin_email: str = "admin@fleet.local"
    seed_superadmin_password: str = "change-me-please"

    # Clave Fernet (32 bytes url-safe base64) para encriptar app.models.gps_provider.GPSProvider.api_credentials_encrypted.
    # Generar una nueva por entorno con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    gps_credentials_encryption_key: str = "JQXVPxHnSxbMkpnW7bNhD3WOFkrV6hYnId_QyerkDjw="

    # Motor de ruteo (Fase 7). "mapbox" usa la Directions API (requiere mapbox_access_token);
    # "fake" es un motor determinista en-memoria para desarrollo/tests sin red. Ver
    # app/routing_engines/. Para migrar a OSRM self-hosted se agrega "osrm" al registry.
    routing_engine: str = "fake"
    mapbox_access_token: str = ""

    # Carpeta local donde se guardan adjuntos de reportes de incidencia (Fase 8). Servida
    # públicamente bajo /uploads (ver app/main.py). Migrar a un bucket S3-compatible más adelante
    # es un cambio acotado a app/core/file_storage.py, sin tocar los endpoints que lo llaman.
    uploads_dir: str = "uploads"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
