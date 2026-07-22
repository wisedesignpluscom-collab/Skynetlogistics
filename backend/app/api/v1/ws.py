import uuid

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.core.websocket_manager import connection_manager
from app.crud import user as user_crud
from app.models.driver import Driver
from app.models.user import User

router = APIRouter(tags=["websocket"])


async def _authenticate(token: str) -> User | None:
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
    async with AsyncSessionLocal() as db:
        user = await user_crud.get_by_id_any_company(db, user_id)
        if user is None or not user.is_active:
            return None
        return user


@router.websocket("/ws/company")
async def company_websocket(websocket: WebSocket, token: str) -> None:
    """Canal en vivo para el despachador: recibe eventos de reportes/chat de toda la empresa.
    Auth por query param (el handshake de WebSocket del navegador no permite headers custom)."""
    user = await _authenticate(token)
    if user is None:
        await websocket.close(code=4401)
        return

    company_id = user.company_id
    await connection_manager.connect_company(company_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect_company(company_id, websocket)


@router.websocket("/ws/driver")
async def driver_websocket(websocket: WebSocket, token: str) -> None:
    """Canal en vivo para el conductor: recibe eventos de sus propios reportes/chat."""
    user = await _authenticate(token)
    if user is None:
        await websocket.close(code=4401)
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Driver).where(Driver.user_id == user.id))
        driver = result.scalar_one_or_none()
    if driver is None:
        await websocket.close(code=4403)
        return

    await connection_manager.connect_driver(driver.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect_driver(driver.id, websocket)
