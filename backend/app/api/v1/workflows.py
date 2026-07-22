import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.crud import workflow as workflow_crud
from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES
from app.models.user import User
from app.schemas.workflow import WorkflowCreate, WorkflowOut, WorkflowUpdate

router = APIRouter(prefix="/workflows", tags=["config"])


@router.get("", response_model=list[WorkflowOut])
async def list_workflows(
    entity_type: str,
    event: str | None = None,
    only_active: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkflowOut]:
    if entity_type not in CUSTOM_FIELD_ENTITY_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "entity_type no soportado")
    return await workflow_crud.list_for_entity(
        db, current_user.company_id, entity_type, event=event, only_active=only_active
    )


@router.post("", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> WorkflowOut:
    return await workflow_crud.create(db, current_user.company_id, payload)


@router.patch("/{workflow_id}", response_model=WorkflowOut)
async def update_workflow(
    workflow_id: uuid.UUID,
    payload: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> WorkflowOut:
    workflow = await workflow_crud.get(db, workflow_id, current_user.company_id)
    if workflow is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workflow no encontrado")
    return await workflow_crud.update(db, workflow, payload)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "delete")),
) -> None:
    workflow = await workflow_crud.get(db, workflow_id, current_user.company_id)
    if workflow is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workflow no encontrado")
    await workflow_crud.delete(db, workflow)
