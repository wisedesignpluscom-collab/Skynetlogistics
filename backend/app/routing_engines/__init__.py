from app.core.config import settings
from app.routing_engines.base import RouteResult, RoutingEngine
from app.routing_engines.fake import FakeRoutingEngine
from app.routing_engines.mapbox import MapboxRoutingEngine, RoutingEngineError

ENGINE_REGISTRY: dict[str, type[RoutingEngine]] = {
    FakeRoutingEngine.engine_name: FakeRoutingEngine,
    MapboxRoutingEngine.engine_name: MapboxRoutingEngine,
}


def get_engine(engine_name: str | None = None) -> RoutingEngine:
    """Devuelve el motor de ruteo activo. Sin argumento usa `settings.routing_engine`
    (por defecto en tests/dev es "fake", que no toca la red)."""
    name = engine_name or settings.routing_engine
    engine_cls = ENGINE_REGISTRY.get(name)
    if engine_cls is None:
        raise ValueError(f"No hay un motor de ruteo registrado para routing_engine='{name}'")
    return engine_cls()


__all__ = [
    "RoutingEngine",
    "RouteResult",
    "RoutingEngineError",
    "FakeRoutingEngine",
    "MapboxRoutingEngine",
    "ENGINE_REGISTRY",
    "get_engine",
]
