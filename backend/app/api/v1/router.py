from fastapi import APIRouter

from app.api.v1 import alerts, auth, companies, drivers, maintenance, providers, roles, users, vehicles

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
