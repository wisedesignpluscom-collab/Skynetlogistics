from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import fatigue_rule as fatigue_rule_crud
from app.models.user import User
from app.schemas.fatigue_rule import FatigueRuleOut, FatigueRuleUpdate

router = APIRouter(prefix="/fatigue-rules", tags=["fatigue"])


@router.get("", response_model=FatigueRuleOut)
async def get_fatigue_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("fatigue", "read")),
) -> FatigueRuleOut:
    return await fatigue_rule_crud.get_or_create(db, current_user.company_id)


@router.patch("", response_model=FatigueRuleOut)
async def update_fatigue_rules(
    payload: FatigueRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("fatigue", "write")),
) -> FatigueRuleOut:
    rule = await fatigue_rule_crud.get_or_create(db, current_user.company_id)
    return await fatigue_rule_crud.update(db, rule, payload)
