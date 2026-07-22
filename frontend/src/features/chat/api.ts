import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { ChatMessage, ChatThread } from '../../types/chat'

export async function getMyGeneralThread(): Promise<ChatThread> {
  const { data } = await api.get<ChatThread>('/chat/my-thread')
  return data
}

export async function getIncidentThread(incidentId: string): Promise<ChatThread> {
  const { data } = await api.get<ChatThread>(`/chat/incident-reports/${incidentId}/thread`)
  return data
}

export async function listChatThreads(params: { page?: number; page_size?: number; status_filter?: string } = {}): Promise<Page<ChatThread>> {
  const { data } = await api.get<Page<ChatThread>>('/chat/threads', { params })
  return data
}

export async function listThreadMessages(threadId: string): Promise<ChatMessage[]> {
  const { data } = await api.get<ChatMessage[]>(`/chat/threads/${threadId}/messages`)
  return data
}

export async function sendThreadMessage(threadId: string, message: string): Promise<ChatMessage> {
  const { data } = await api.post<ChatMessage>(`/chat/threads/${threadId}/messages`, { message })
  return data
}

export async function closeThread(threadId: string): Promise<ChatThread> {
  const { data } = await api.patch<ChatThread>(`/chat/threads/${threadId}`, { status: 'cerrado' })
  return data
}
