import { useFormRules, type FormRulesResult } from './useFormRules'
import type { CustomData, CustomFieldEntityType } from '../../types/customField'

/** Arma el contexto de evaluación (campos de sistema + custom aplanados como `custom.<key>`) y
 *  evalúa las reglas de formulario activas de la entidad — una sola vez por formulario. El objeto
 *  devuelto se usa tanto para controlar los campos de sistema del formulario host como para pasarlo
 *  a `CustomFieldsSection` (evita una segunda carga/evaluación de las mismas reglas). */
export function useSystemFieldRules(
  entityType: CustomFieldEntityType,
  systemValues: Record<string, unknown>,
  customData: CustomData
): FormRulesResult {
  const context: Record<string, unknown> = { ...systemValues }
  for (const [k, v] of Object.entries(customData)) context[`custom.${k}`] = v
  return useFormRules(entityType, context)
}
