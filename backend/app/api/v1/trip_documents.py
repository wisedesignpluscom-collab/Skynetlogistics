import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver as driver_crud
from app.crud import trip as trip_crud
from app.crud import trip_expense as trip_expense_crud
from app.crud import vehicle as vehicle_crud
from app.models.user import User

router = APIRouter(prefix="/trips", tags=["trips"])

_PRINT_STYLES = """
<style>
  * { box-sizing: border-box; }
  body { font-family: Georgia, 'Times New Roman', serif; color: #111; margin: 2rem; }
  h1 { font-size: 1.4rem; border-bottom: 2px solid #111; padding-bottom: 0.5rem; }
  table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
  th, td { text-align: left; padding: 0.4rem 0.6rem; border: 1px solid #999; font-size: 0.9rem; }
  th { background: #eee; }
  .meta { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 2rem; margin: 1rem 0; }
  .meta div { font-size: 0.95rem; }
  .meta b { display: inline-block; min-width: 140px; }
  .total { font-weight: bold; font-size: 1.05rem; }
  @media print {
    body { margin: 0.5in; }
  }
</style>
"""


async def _get_trip_with_relations(db: AsyncSession, trip_id: uuid.UUID, company_id: uuid.UUID):
    trip = await trip_crud.get(db, trip_id, company_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")
    vehicle = await vehicle_crud.get(db, trip.vehicle_id, company_id)
    driver = await driver_crud.get(db, trip.driver_id, company_id)
    trailer = await vehicle_crud.get(db, trip.trailer_id, company_id) if trip.trailer_id else None
    return trip, vehicle, driver, trailer


@router.get("/{trip_id}/documents/loading-order", response_class=HTMLResponse)
async def get_loading_order_document(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> str:
    trip, vehicle, driver, trailer = await _get_trip_with_relations(db, trip_id, current_user.company_id)

    return f"""
    <!doctype html>
    <html lang="es"><head><meta charset="utf-8"><title>Orden de Carga — {trip.origin} → {trip.destination}</title>
    {_PRINT_STYLES}</head>
    <body>
      <h1>Orden de Carga</h1>
      <div class="meta">
        <div><b>Origen:</b> {trip.origin}</div>
        <div><b>Destino:</b> {trip.destination}</div>
        <div><b>Vehículo:</b> {vehicle.plate} — {vehicle.brand} {vehicle.model}</div>
        <div><b>Remolque:</b> {trailer.plate if trailer else '—'}</div>
        <div><b>Conductor:</b> {driver.name}</div>
        <div><b>Licencia:</b> {driver.license_number}</div>
        <div><b>Tipo de carga:</b> {trip.cargo_type}</div>
        <div><b>Distancia estimada:</b> {trip.distance_km or '—'} km</div>
        <div><b>Ida y vuelta:</b> {'Sí' if trip.is_round_trip else 'No'}</div>
        <div><b>Estado:</b> {trip.status}</div>
      </div>
      <p class="total">Flete: ${trip.freight_cost if trip.freight_cost is not None else '—'}</p>
    </body></html>
    """


@router.get("/{trip_id}/documents/expense-receipt", response_class=HTMLResponse)
async def get_expense_receipt_document(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> str:
    trip, vehicle, driver, _trailer = await _get_trip_with_relations(db, trip_id, current_user.company_id)
    expenses = await trip_expense_crud.list_for_trip(db, trip_id)

    rows = "".join(
        f"<tr><td>{e.concept.name}</td><td>{e.notes or ''}</td><td>${e.amount}</td></tr>" for e in expenses
    )
    total = sum(float(e.amount) for e in expenses)

    return f"""
    <!doctype html>
    <html lang="es"><head><meta charset="utf-8"><title>Recibo de Viáticos — {trip.origin} → {trip.destination}</title>
    {_PRINT_STYLES}</head>
    <body>
      <h1>Recibo de Viáticos</h1>
      <div class="meta">
        <div><b>Conductor:</b> {driver.name}</div>
        <div><b>Vehículo:</b> {vehicle.plate}</div>
        <div><b>Ruta:</b> {trip.origin} → {trip.destination}</div>
        <div><b>Estado:</b> {trip.status}</div>
      </div>
      <table>
        <thead><tr><th>Concepto</th><th>Notas</th><th>Monto</th></tr></thead>
        <tbody>{rows or '<tr><td colspan="3">Sin gastos registrados.</td></tr>'}</tbody>
      </table>
      <p class="total">Total: ${total:.2f}</p>
    </body></html>
    """
