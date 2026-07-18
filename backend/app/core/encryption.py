import json
from typing import Any

from cryptography.fernet import Fernet

from app.core.config import settings


def _get_fernet() -> Fernet:
    return Fernet(settings.gps_credentials_encryption_key.encode("utf-8"))


def encrypt_credentials(credentials: dict[str, Any]) -> bytes:
    return _get_fernet().encrypt(json.dumps(credentials).encode("utf-8"))


def decrypt_credentials(encrypted: bytes) -> dict[str, Any]:
    return json.loads(_get_fernet().decrypt(encrypted).decode("utf-8"))
