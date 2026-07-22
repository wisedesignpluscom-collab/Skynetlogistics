import { api } from '../../lib/axios'
import type { CustomFieldEntityType } from '../../types/customField'
import type { Workflow, WorkflowAction, WorkflowEvent } from '../../types/workflow'
import type { RuleCondition } from './ruleEngine'

export interface WorkflowCreatePayload {
  entity_type: CustomFieldEntityType
  event: WorkflowEvent
  name: string
  condition: RuleCondition
  actions: WorkflowAction[]
  active?: boolean
  order?: number
}

export interface WorkflowUpdatePayload {
  name?: string
  condition?: RuleCondition
  actions?: WorkflowAction[]
  active?: boolean
  order?: number
}

export async function listWorkflows(
  entityType: CustomFieldEntityType,
  opts: { event?: WorkflowEvent; onlyActive?: boolean } = {}
): Promise<Workflow[]> {
  const { data } = await api.get<Workflow[]>('/workflows', {
    params: { entity_type: entityType, event: opts.event, only_active: opts.onlyActive },
  })
  return data
}

export async function createWorkflow(payload: WorkflowCreatePayload): Promise<Workflow> {
  const { data } = await api.post<Workflow>('/workflows', payload)
  return data
}

export async function updateWorkflow(id: string, payload: WorkflowUpdatePayload): Promise<Workflow> {
  const { data } = await api.patch<Workflow>(`/workflows/${id}`, payload)
  return data
}

export async function deleteWorkflow(id: string): Promise<void> {
  await api.delete(`/workflows/${id}`)
}
