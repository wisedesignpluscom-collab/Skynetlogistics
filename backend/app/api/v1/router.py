from fastapi import APIRouter

from app.api.v1 import (
    alerts,
    auth,
    companies,
    driver_pay_rates,
    drivers,
    expense_concepts,
    holidays,
    maintenance,
    providers,
    rate_tables,
    roles,
    trip_documents,
    trips,
    users,
    vehicles,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(vehicles.router)
api_router.include_router(drivers.router)
api_router.include_router(providers.router)
api_router.include_router(maintenance.router)
api_router.include_router(alerts.router)
api_router.include_router(rate_tables.router)
api_router.include_router(driver_pay_rates.router)
api_router.include_router(holidays.router)
api_router.include_router(expense_concepts.router)
api_router.include_router(trips.router)
api_router.include_router(trip_documents.router)
