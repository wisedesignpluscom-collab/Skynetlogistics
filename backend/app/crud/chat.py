import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatThread


async def get_thread(db: AsyncSession, thread_id: uuid.UUID, company_id: uuid.UUID) -> ChatThread | None:
    result = await db.execute(
        select(ChatThread).where(ChatThread.id == thread_id, ChatThread.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_thread(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    driver_id: uuid.UUID,
    incident_report_id: uuid.UUID | None = None,
) -> ChatThread:
    """Un hilo por (driver_id, incident_report_id): si `incident_report_id` es None es el chat
    general de dudas del conductor (uno solo, se reutiliza); si no, el hilo atado a ese reporte."""
    query = select(ChatThread).where(
        ChatThread.company_id == company_id,
        ChatThread.driver_id == driver_id,
        ChatThread.incident_report_id == incident_report_id,
    )
    result = await db.execute(query)
    thread = result.scalar_one_or_none()
    if thread is not None:
        return thread

    thread = ChatThread(company_id=company_id, driver_id=driver_id, incident_report_id=incident_report_id)
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return thread


async def list_threads_for_driver(db: AsyncSession, driver_id: uuid.UUID, company_id: uuid.UUID) -> list[ChatThread]:
    result = await db.execute(
        select(ChatThread)
        .where(ChatThread.company_id == company_id, ChatThread.driver_id == driver_id)
        .order_by(ChatThread.created_at.desc())
    )
    return list(result.scalars().all())


async def list_threads_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
) -> tuple[list[ChatThread], int]:
    query = select(ChatThread).where(ChatThread.company_id == company_id)
    count_query = select(func.count()).select_from(ChatThread).where(ChatThread.company_id == company_id)
    if status:
        query = query.where(ChatThread.status == status)
        count_query = count_query.where(ChatThread.status == status)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(ChatThread.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def close_thread(db: AsyncSession, thread: ChatThread) -> ChatThread:
    thread.status = "cerrado"
    await db.commit()
    await db.refresh(thread)
    return thread


async def create_message(
    db: AsyncSession, *, thread_id: uuid.UUID, sender_type: str, sender_id: uuid.UUID, message: str
) -> ChatMessage:
    chat_message = ChatMessage(thread_id=thread_id, sender_type=sender_type, sender_id=sender_id, message=message)
    db.add(chat_message)
    await db.commit()
    await db.refresh(chat_message)
    return chat_message


async def list_messages(db: AsyncSession, thread_id: uuid.UUID) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())
