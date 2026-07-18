import { api } from '../../lib/axios'
import type {
  GPSProvider,
  GPSProviderCreated,
  GPSProviderVehicleMap,
  IngestionMode,
  VehiclePosition,
} from '../../types/gps'

export interface GPSProviderPayload {
  provider_name: string
  adapter_type: string
  api_credentials: Record<string, unknown>
  ingestion_mode: IngestionMode
  polling_interval_seconds?: number | null
}

export async function listGpsProviders(): Promise<GPSProvider[]> {
  const { data } = await api.get<GPSProvider[]>('/gps-providers')
  return data
}

export async function createGpsProvider(payload: GPSProviderPayload): Promise<GPSProviderCreated> {
  const { data } = await api.post<GPSProviderCreated>('/gps-providers', payload)
  return data
}

export async function deleteGpsProvider(id: string): Promise<void> {
  await api.delete(`/gps-providers/${id}`)
}

export async function regenerateWebhookToken(id: string): Promise<GPSProviderCreated> {
  const { data } = await api.post<GPSProviderCreated>(`/gps-providers/${id}/regenerate-token`)
  return data
}

export async function listVehicleMap(providerId: string): Promise<GPSProviderVehicleMap[]> {
  const { data } = await api.get<GPSProviderVehicleMap[]>(`/gps-providers/${providerId}/vehicle-map`)
  return data
}

export async function createVehicleMap(
  providerId: string,
  payload: { vehicle_id: string; external_device_id: string },
): Promise<GPSProviderVehicleMap> {
  const { data } = await api.post<GPSProviderVehicleMap>(`/gps-providers/${providerId}/vehicle-map`, payload)
  return data
}

export async function deleteVehicleMap(providerId: string, mappingId: string): Promise<void> {
  await api.delete(`/gps-providers/${providerId}/vehicle-map/${mappingId}`)
}

export async function getFleetLatestPositions(): Promise<VehiclePosition[]> {
  const { data } = await api.get<VehiclePosition[]>('/fleet/positions/latest')
  return data
}

export async function getLatestPosition(vehicleId: string): Promise<VehiclePosition | null> {
  const { data } = await api.get<VehiclePosition | null>(`/vehicles/${vehicleId}/position/latest`)
  return data
}

export async function getPositionHistory(
  vehicleId: string,
  dateFrom: string,
  dateTo: string,
): Promise<VehiclePosition[]> {
  const { data } = await api.get<VehiclePosition[]>(`/vehicles/${vehicleId}/positions`, {
    params: { date_from: dateFrom, date_to: dateTo },
  })
  return data
}
