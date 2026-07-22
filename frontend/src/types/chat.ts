export type ChatThreadStatus = 'abierto' | 'cerrado'
export type ChatMessageSenderType = 'conductor' | 'despachador'

export interface ChatThread {
  id: string
  company_id: string
  driver_id: string
  incident_report_id: string | null
  status: ChatThreadStatus
  created_at: string
}

export interface ChatMessage {
  id: string
  thread_id: string
  sender_type: ChatMessageSenderType
  sender_id: string
  message: string
  created_at: string
}
