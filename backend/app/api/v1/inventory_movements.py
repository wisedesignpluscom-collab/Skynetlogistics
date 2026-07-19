import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import inventory_item as inventory_item_crud
from app.crud import inventory_movement as inventory_movement_crud
from app.models.user import User
from app.schemas.inventory_item import InventoryMovementCreate, InventoryMovementOut
from app.services.inventory_movements import InvalidInventoryMovement, apply_movement

router = APIRouter(prefix="/inventory-movements", tags=["inventory"])


@router.get("", response_model=list[InventoryMovementOut])
async def list_inventory_movements(
    item_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "read")),
) -> list[InventoryMovementOut]:
    return await inventory_movement_crud.list_filtered(
        db, company_id=current_user.company_id, item_id=item_id, vehicle_id=vehicle_id
    )


@router.post("", response_model=InventoryMovementOut, status_code=status.HTTP_201_CREATED)
async def create_inventory_movement(
    payload: InventoryMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "write")),
) -> InventoryMovementOut:
    item = await inventory_item_crud.get(db, payload.item_id, current_user.company_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ítem de inventario no encontrado")

    try:
        return await apply_movement(
            db,
            item,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            vehicle_id=payload.vehicle_id,
            unit_cost=payload.unit_cost,
            reference_doc=payload.reference_doc,
            notes=payload.notes,
            recorded_by=current_user.id,
        )
    except InvalidInventoryMovement as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
