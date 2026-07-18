from app.gps_adapters.base import GPSProviderAdapter, NormalizedPosition
from app.gps_adapters.traker_gps import TrakerGPSAdapter

ADAPTER_REGISTRY: dict[str, type[GPSProviderAdapter]] = {
    TrakerGPSAdapter.adapter_type: TrakerGPSAdapter,
}


def get_adapter(adapter_type: str) -> GPSProviderAdapter:
    adapter_cls = ADAPTER_REGISTRY.get(adapter_type)
    if adapter_cls is None:
        raise ValueError(f"No hay un adapter registrado para adapter_type='{adapter_type}'")
    return adapter_cls()


__all__ = ["GPSProviderAdapter", "NormalizedPosition", "ADAPTER_REGISTRY", "get_adapter"]
