import { api } from '../../lib/axios'
import type { VehicleDocument, VehicleDocumentType } from '../../types/vehicle_document'

export interface VehicleDocumentTypePayload {
  name: string
  alert_days_before?: number
}

export interface VehicleDocumentPayload {
  document_type_id: string
  number?: string | null
  expiry_date?: string | null
  notes?: string | null
}

export async function listVehicleDocumentTypes(): Promise<VehicleDocumentType[]> {
  const { data } = await api.get<VehicleDocumentType[]>('/vehicle-document-types')
  return data
}

export async function createVehicleDocumentType(
  payload: VehicleDocumentTypePayload,
): Promise<VehicleDocumentType> {
  const { data } = await api.post<VehicleDocumentType>('/vehicle-document-types', payload)
  return data
}

export async function listVehicleDocuments(vehicleId: string): Promise<VehicleDocument[]> {
  const { data } = await api.get<VehicleDocument[]>(`/vehicles/${vehicleId}/documents`)
  return data
}

export async function createVehicleDocument(
  vehicleId: string,
  payload: VehicleDocumentPayload,
): Promise<VehicleDocument> {
  const { data } = await api.post<VehicleDocument>(`/vehicles/${vehicleId}/documents`, payload)
  return data
}

export async function deleteVehicleDocument(id: string): Promise<void> {
  await api.delete(`/vehicle-documents/${id}`)
}
