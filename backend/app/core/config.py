from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"

    database_url: str = "postgresql+asyncpg://fleet:fleet_dev_pw@localhost:5432/fleet_db"

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

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
