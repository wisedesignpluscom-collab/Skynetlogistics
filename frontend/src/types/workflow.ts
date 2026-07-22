import type { CustomFieldEntityType } from './customField'
import type { RuleCondition } from '../features/config/ruleEngine'

export type WorkflowEvent = 'creado' | 'actualizado' | 'cambio_estado'
export const WORKFLOW_EVENT_LABELS: Record<WorkflowEvent, string> = {
  creado: 'Se crea el registro',
  actualizado: 'Se actualiza el registro',
  cambio_estado: 'Cambia de estado',
}

export type WorkflowActionType = 'crear_alerta' | 'actualizar_campo'

export interface WorkflowAction {
  type: WorkflowActionType
  message?: string | null // crear_alerta
  severity?: 'baja' | 'media' | 'alta' | null // crear_alerta
  target?: string | null // actualizar_campo (custom.<key>)
  value?: string | number | boolean | null // actualizar_campo
}

export interface Workflow {
  id: string
  company_id: string
  entity_type: CustomFieldEntityType
  name: string
  event: WorkflowEvent
  condition: RuleCondition
  actions: WorkflowAction[]
  active: boolean
  order: number
  created_at: string
  updated_at: string
}
