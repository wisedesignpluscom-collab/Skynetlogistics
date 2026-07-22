import uuid

from fastapi import WebSocket

# ConnectionManager en memoria, un solo proceso — mismo criterio que el AsyncIOScheduler de
# app/main.py (sin Redis/pubsub; si en el futuro el backend corre en múltiples instancias, esto
# necesita moverse a un pubsub compartido, pero no antes de que ese escenario sea real).


class ConnectionManager:
    def __init__(self) -> None:
        self._company_connections: dict[uuid.UUID, set[WebSocket]] = {}
        self._driver_connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect_company(self, company_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._company_connections.setdefault(company_id, set()).add(websocket)

    async def connect_driver(self, driver_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._driver_connections.setdefault(driver_id, set()).add(websocket)

    def disconnect_company(self, company_id: uuid.UUID, websocket: WebSocket) -> None:
        self._company_connections.get(company_id, set()).discard(websocket)

    def disconnect_driver(self, driver_id: uuid.UUID, websocket: WebSocket) -> None:
        self._driver_connections.get(driver_id, set()).discard(websocket)

    async def broadcast_to_company(self, company_id: uuid.UUID, payload: dict) -> None:
        for websocket in list(self._company_connections.get(company_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:
                self._company_connections[company_id].discard(websocket)

    async def broadcast_to_driver(self, driver_id: uuid.UUID, payload: dict) -> None:
        for websocket in list(self._driver_connections.get(driver_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:
                self._driver_connections[driver_id].discard(websocket)


connection_manager = ConnectionManager()
