import { api } from '../../lib/axios'
import type { CustomFieldEntityType } from '../../types/customField'
import type { EntitySchema, FormRule, FormRuleKind, RuleAction } from '../../types/formRule'
import type { RuleCondition } from './ruleEngine'

export interface FormRuleCreatePayload {
  entity_type: CustomFieldEntityType
  kind: FormRuleKind
  name: string
  condition: RuleCondition
  actions: RuleAction[]
  active?: boolean
  order?: number
}

export interface FormRuleUpdatePayload {
  name?: string
  condition?: RuleCondition
  actions?: RuleAction[]
  active?: boolean
  order?: number
}

export async function getEntitySchema(entityType: CustomFieldEntityType): Promise<EntitySchema> {
  const { data } = await api.get<EntitySchema>('/form-rules/entity-schema', {
    params: { entity_type: entityType },
  })
  return data
}

export async function listFormRules(
  entityType: CustomFieldEntityType,
  opts: { kind?: FormRuleKind; onlyActive?: boolean } = {}
): Promise<FormRule[]> {
  const { data } = await api.get<FormRule[]>('/form-rules', {
    params: { entity_type: entityType, kind: opts.kind, only_active: opts.onlyActive },
  })
  return data
}

export async function createFormRule(payload: FormRuleCreatePayload): Promise<FormRule> {
  const { data } = await api.post<FormRule>('/form-rules', payload)
  return data
}

export async function updateFormRule(id: string, payload: FormRuleUpdatePayload): Promise<FormRule> {
  const { data } = await api.patch<FormRule>(`/form-rules/${id}`, payload)
  return data
}

export async function deleteFormRule(id: string): Promise<void> {
  await api.delete(`/form-rules/${id}`)
}
