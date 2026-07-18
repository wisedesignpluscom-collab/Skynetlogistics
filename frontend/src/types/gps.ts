export type IngestionMode = 'webhook' | 'polling'

export interface GPSProvider {
  id: string
  company_id: string
  provider_name: string
  adapter_type: string
  ingestion_mode: IngestionMode
  polling_interval_seconds: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface GPSProviderCreated extends GPSProvider {
  webhook_token: string | null
}

export interface GPSProviderVehicleMap {
  id: string
  provider_id: string
  vehicle_id: string
  external_device_id: string
  created_at: string
}

export interface VehiclePosition {
  id: string
  vehicle_id: string
  company_id: string
  provider_id: string
  timestamp: string
  lat: number
  lng: number
  speed_kmh: number | null
  odometer_km: number | null
  ignition_status: boolean | null
  heading: number | null
}
