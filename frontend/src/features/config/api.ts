import { api } from '../../lib/axios'
import type {
  CustomFieldDefinition,
  CustomFieldEntityType,
  CustomFieldOption,
  CustomFieldType,
} from '../../types/customField'

export interface CustomFieldCreatePayload {
  entity_type: CustomFieldEntityType
  key: string
  label: string
  field_type: CustomFieldType
  options?: CustomFieldOption[]
  required?: boolean
  order?: number
  active?: boolean
  help_text?: string | null
}

export interface CustomFieldUpdatePayload {
  label?: string
  options?: CustomFieldOption[]
  required?: boolean
  order?: number
  active?: boolean
  help_text?: string | null
}

export async function listCustomFields(
  entityType: CustomFieldEntityType,
  onlyActive = false
): Promise<CustomFieldDefinition[]> {
  const { data } = await api.get<CustomFieldDefinition[]>('/custom-fields', {
    params: { entity_type: entityType, only_active: onlyActive },
  })
  return data
}

export async function createCustomField(payload: CustomFieldCreatePayload): Promise<CustomFieldDefinition> {
  const { data } = await api.post<CustomFieldDefinition>('/custom-fields', payload)
  return data
}

export async function updateCustomField(
  id: string,
  payload: CustomFieldUpdatePayload
): Promise<CustomFieldDefinition> {
  const { data } = await api.patch<CustomFieldDefinition>(`/custom-fields/${id}`, payload)
  return data
}

export async function deleteCustomField(id: string): Promise<void> {
  await api.delete(`/custom-fields/${id}`)
}
