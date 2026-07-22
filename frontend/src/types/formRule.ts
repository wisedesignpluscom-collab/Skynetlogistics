import type { CustomFieldEntityType } from './customField'
import type { RuleCondition } from '../features/config/ruleEngine'

export type FormRuleKind = 'formulario' | 'validacion'

export type FormActionType = 'mostrar' | 'ocultar' | 'requerir' | 'opcional' | 'calcular'
export type RuleActionType = FormActionType | 'bloquear'

export interface RuleAction {
  type: RuleActionType
  target?: string | null // campo objetivo (reglas de formulario)
  formula?: string | null // solo "calcular"
  message?: string | null // solo "bloquear"
}

export interface FormRule {
  id: string
  company_id: string
  entity_type: CustomFieldEntityType
  name: string
  kind: FormRuleKind
  condition: RuleCondition
  actions: RuleAction[]
  active: boolean
  order: number
  created_at: string
  updated_at: string
}

export interface EntityField {
  key: string
  label: string
  type: string
  options: { value: string; label: string }[]
  source: 'sistema' | 'custom'
}

export interface EntitySchema {
  entity_type: CustomFieldEntityType
  fields: EntityField[]
}
