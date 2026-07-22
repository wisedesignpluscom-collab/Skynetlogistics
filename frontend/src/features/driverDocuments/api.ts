import { api } from '../../lib/axios'
import type { DriverDocument, DriverDocumentType } from '../../types/driver_document'

export interface DriverDocumentTypePayload {
  name: string
  alert_days_before?: number
}

export interface DriverDocumentPayload {
  document_type_id: string
  number?: string | null
  expiry_date?: string | null
  notes?: string | null
}

export async function listDriverDocumentTypes(): Promise<DriverDocumentType[]> {
  const { data } = await api.get<DriverDocumentType[]>('/driver-document-types')
  return data
}

export async function createDriverDocumentType(
  payload: DriverDocumentTypePayload,
): Promise<DriverDocumentType> {
  const { data } = await api.post<DriverDocumentType>('/driver-document-types', payload)
  return data
}

export async function deleteDriverDocumentType(id: string): Promise<void> {
  await api.delete(`/driver-document-types/${id}`)
}

export async function listDriverDocuments(driverId: string): Promise<DriverDocument[]> {
  const { data } = await api.get<DriverDocument[]>(`/drivers/${driverId}/documents`)
  return data
}

export async function createDriverDocument(
  driverId: string,
  payload: DriverDocumentPayload,
): Promise<DriverDocument> {
  const { data } = await api.post<DriverDocument>(`/drivers/${driverId}/documents`, payload)
  return data
}

export async function updateDriverDocument(
  id: string,
  payload: Partial<DriverDocumentPayload>,
): Promise<DriverDocument> {
  const { data } = await api.patch<DriverDocument>(`/driver-documents/${id}`, payload)
  return data
}

export async function deleteDriverDocument(id: string): Promise<void> {
  await api.delete(`/driver-documents/${id}`)
}
