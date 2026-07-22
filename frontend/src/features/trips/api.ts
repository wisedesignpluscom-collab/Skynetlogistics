import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type {
  Trip,
  TripClosePreview,
  TripExpense,
  TripStatus,
  TripWithDetails,
} from '../../types/trip'

export interface TripListParams {
  page?: number
  page_size?: number
  status_filter?: TripStatus
  driver_id?: string
  vehicle_id?: string
  date_from?: string
  date_to?: string
}

export interface TripPayload {
  vehicle_id: string
  driver_id: string
  trailer_id?: string | null
  client_id?: string | null
  origin: string
  destination: string
  cargo_type: string
  is_round_trip?: boolean
  // Coordenadas opcionales (Fase 7): si vienen las 4, al crear el viaje se calcula la ruta.
  origin_lat?: number | null
  origin_lng?: number | null
  destination_lat?: number | null
  destination_lng?: number | null
  custom_data?: Record<string, unknown>
}

export interface TripUpdatePayload {
  origin?: string
  destination?: string
  cargo_type?: string
  is_round_trip?: boolean
  distance_km?: number
  freight_cost?: number
}

export interface TripClosePayload {
  end_odometer_km: number
  freight_cost?: number | null
  advance_payment?: number | null
}

export async function listTrips(params: TripListParams = {}): Promise<Page<Trip>> {
  const { data } = await api.get<Page<Trip>>('/trips', { params })
  return data
}

export async function getTrip(id: string): Promise<TripWithDetails> {
  const { data } = await api.get<TripWithDetails>(`/trips/${id}`)
  return data
}

export async function createTrip(payload: TripPayload): Promise<Trip> {
  const { data } = await api.post<Trip>('/trips', payload)
  return data
}

export async function updateTrip(id: string, payload: TripUpdatePayload): Promise<Trip> {
  const { data } = await api.patch<Trip>(`/trips/${id}`, payload)
  return data
}

export async function startTrip(id: string, startOdometerKm: number): Promise<Trip> {
  const { data } = await api.post<Trip>(`/trips/${id}/start`, { start_odometer_km: startOdometerKm })
  return data
}

export async function setTripAdvance(id: string, advancePayment: number): Promise<Trip> {
  const { data } = await api.patch<Trip>(`/trips/${id}/advance`, { advance_payment: advancePayment })
  return data
}

export async function createTripExpense(
  tripId: string,
  payload: { concept_id: string; amount: number; notes?: string | null },
): Promise<TripExpense> {
  const { data } = await api.post<TripExpense>(`/trips/${tripId}/expenses`, payload)
  return data
}

export async function deleteTripExpense(tripId: string, expenseId: string): Promise<void> {
  await api.delete(`/trips/${tripId}/expenses/${expenseId}`)
}

export async function getTripClosePreview(id: string): Promise<TripClosePreview> {
  const { data } = await api.get<TripClosePreview>(`/trips/${id}/close-preview`)
  return data
}

export async function closeTrip(id: string, payload: TripClosePayload): Promise<TripWithDetails> {
  const { data } = await api.post<TripWithDetails>(`/trips/${id}/close`, payload)
  return data
}

export async function cancelTrip(id: string): Promise<Trip> {
  const { data } = await api.post<Trip>(`/trips/${id}/cancel`)
  return data
}
