import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type {
  IncidentReport,
  IncidentReportAttachment,
  IncidentReportCreatePayload,
  IncidentStatus,
} from '../../types/incident'

export interface IncidentReportListParams {
  page?: number
  page_size?: number
  status_filter?: IncidentStatus
  severity?: string
  type?: string
  driver_id?: string
}

export async function listIncidentReports(params: IncidentReportListParams = {}): Promise<Page<IncidentReport>> {
  const { data } = await api.get<Page<IncidentReport>>('/incident-reports', { params })
  return data
}

export async function listMyIncidentReports(): Promise<IncidentReport[]> {
  const { data } = await api.get<IncidentReport[]>('/incident-reports/mine')
  return data
}

export async function getIncidentReport(id: string): Promise<IncidentReport> {
  const { data } = await api.get<IncidentReport>(`/incident-reports/${id}`)
  return data
}

export async function createIncidentReport(payload: IncidentReportCreatePayload): Promise<IncidentReport> {
  const { data } = await api.post<IncidentReport>('/incident-reports', payload)
  return data
}

export async function updateIncidentReportStatus(
  id: string,
  payload: { status: IncidentStatus; resolution_notes?: string | null },
): Promise<IncidentReport> {
  const { data } = await api.patch<IncidentReport>(`/incident-reports/${id}`, payload)
  return data
}

export async function listIncidentReportAttachments(id: string): Promise<IncidentReportAttachment[]> {
  const { data } = await api.get<IncidentReportAttachment[]>(`/incident-reports/${id}/attachments`)
  return data
}

export async function uploadIncidentReportAttachment(
  id: string,
  file: File,
): Promise<IncidentReportAttachment> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<IncidentReportAttachment>(`/incident-reports/${id}/attachments`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
