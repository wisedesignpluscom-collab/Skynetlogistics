import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_ATTACHMENT_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


async def save_incident_attachment(company_id: uuid.UUID, incident_report_id: uuid.UUID, file: UploadFile) -> str:
    """Guarda un adjunto en disco bajo uploads/<company_id>/incidents/<incident_id>/ y devuelve
    la ruta pública servida por /uploads (ver StaticFiles mount en app/main.py)."""
    if file.content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
        raise ValueError(f"Tipo de archivo no permitido: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValueError("El archivo supera el tamaño máximo permitido (10 MB)")

    extension = Path(file.filename or "").suffix
    filename = f"{uuid.uuid4()}{extension}"
    relative_dir = Path(str(company_id)) / "incidents" / str(incident_report_id)
    target_dir = Path(settings.uploads_dir) / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / filename
    target_path.write_bytes(contents)

    return f"/uploads/{relative_dir.as_posix()}/{filename}"
