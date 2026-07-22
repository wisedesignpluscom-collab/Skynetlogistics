import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_driver, require_permission
from app.core.websocket_manager import connection_manager
from app.crud import chat as chat_crud
from app.crud import incident_report as incident_report_crud
from app.models.chat import ChatThread
from app.models.driver import Driver
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageOut, ChatThreadOut, ChatThreadUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/chat", tags=["chat"])


async def _get_own_driver_or_none(db: AsyncSession, current_user: User) -> Driver | None:
    result = await db.execute(select(Driver).where(Driver.user_id == current_user.id))
    return result.scalar_one_or_none()


async def _get_thread_for_user_or_403(
    db: AsyncSession, thread_id: uuid.UUID, current_user: User, current_driver: Driver | None
) -> ChatThread:
    thread = await chat_crud.get_thread(db, thread_id, current_user.company_id)
    if thread is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hilo no encontrado")
    if current_driver is not None and thread.driver_id != current_driver.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este hilo no te pertenece")
    return thread


@router.get("/threads", response_model=Page[ChatThreadOut])
async def list_chat_threads(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "read")),
) -> Page[ChatThreadOut]:
    items, total = await chat_crud.list_threads_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size, status=status_filter
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/my-thread", response_model=ChatThreadOut)
async def get_my_general_thread(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "write")),
    current_driver: Driver = Depends(get_current_driver),
) -> ChatThreadOut:
    """Chat general de dudas del conductor (sin incident_report_id) — se crea la primera vez que
    el conductor lo abre."""
    return await chat_crud.get_or_create_thread(
        db, company_id=current_user.company_id, driver_id=current_driver.id
    )


@router.get("/incident-reports/{incident_id}/thread", response_model=ChatThreadOut)
async def get_incident_thread(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "read")),
) -> ChatThreadOut:
    incident = await incident_report_crud.get(db, incident_id, current_user.company_id)
    if incident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    return await chat_crud.get_or_create_thread(
        db, company_id=current_user.company_id, driver_id=incident.driver_id, incident_report_id=incident_id
    )


@router.get("/threads/{thread_id}/messages", response_model=list[ChatMessageOut])
async def list_thread_messages(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "read")),
) -> list[ChatMessageOut]:
    current_driver = await _get_own_driver_or_none(db, current_user)
    thread = await _get_thread_for_user_or_403(db, thread_id, current_user, current_driver)
    return await chat_crud.list_messages(db, thread.id)


@router.post("/threads/{thread_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def create_thread_message(
    thread_id: uuid.UUID,
    payload: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "write")),
) -> ChatMessageOut:
    current_driver = await _get_own_driver_or_none(db, current_user)
    thread = await _get_thread_for_user_or_403(db, thread_id, current_user, current_driver)

    sender_type = "conductor" if current_driver is not None else "despachador"
    sender_id = current_driver.id if current_driver is not None else current_user.id

    message = await chat_crud.create_message(
        db, thread_id=thread.id, sender_type=sender_type, sender_id=sender_id, message=payload.message
    )

    event = {
        "event": "chat_message",
        "thread_id": str(thread.id),
        "message": {
            "id": str(message.id),
            "sender_type": message.sender_type,
            "message": message.message,
            "created_at": message.created_at.isoformat(),
        },
    }
    await connection_manager.broadcast_to_driver(thread.driver_id, event)
    await connection_manager.broadcast_to_company(current_user.company_id, event)
    return message


@router.patch("/threads/{thread_id}", response_model=ChatThreadOut)
async def close_thread(
    thread_id: uuid.UUID,
    payload: ChatThreadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("chat", "write")),
) -> ChatThreadOut:
    thread = await chat_crud.get_thread(db, thread_id, current_user.company_id)
    if thread is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hilo no encontrado")
    if payload.status != "cerrado":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Solo se puede cerrar un hilo desde este endpoint")
    return await chat_crud.close_thread(db, thread)
