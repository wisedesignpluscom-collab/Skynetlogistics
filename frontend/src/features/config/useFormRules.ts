import { useEffect, useMemo, useState } from 'react'
import { listFormRules } from './rulesApi'
import { evaluateCondition, evaluateFormula, type RuleContext } from './ruleEngine'
import type { CustomFieldEntityType } from '../../types/customField'
import type { FormRule } from '../../types/formRule'

export interface FormRulesResult {
  isHidden: (fieldKey: string) => boolean
  isRequired: (fieldKey: string) => boolean
  computed: Record<string, number>
  loaded: boolean
}

/** Carga las reglas de formulario activas de la entidad y las evalúa contra `context` (valores del
 *  formulario, con los custom aplanados como `custom.<key>`). Devuelve helpers para saber si un
 *  campo debe ocultarse / requerirse y los valores calculados. Recalcula cuando cambia `context`. */
export function useFormRules(
  entityType: CustomFieldEntityType | undefined,
  context: RuleContext
): FormRulesResult {
  const [rules, setRules] = useState<FormRule[]>([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (!entityType) return
    let active = true
    void listFormRules(entityType, { kind: 'formulario', onlyActive: true }).then((r) => {
      if (active) {
        setRules(r)
        setLoaded(true)
      }
    })
    return () => {
      active = false
    }
  }, [entityType])

  const contextKey = JSON.stringify(context)

  return useMemo(() => {
    const ctx: RuleContext = JSON.parse(contextKey)
    const hidden = new Set<string>()
    const shown = new Set<string>()
    const required = new Set<string>()
    const optional = new Set<string>()
    const computed: Record<string, number> = {}

    for (const rule of rules) {
      if (!evaluateCondition(rule.condition, ctx)) continue
      for (const action of rule.actions) {
        const target = action.target ?? ''
        if (action.type === 'ocultar') hidden.add(target)
        else if (action.type === 'mostrar') shown.add(target)
        else if (action.type === 'requerir') required.add(target)
        else if (action.type === 'opcional') optional.add(target)
        else if (action.type === 'calcular' && action.formula) {
          const v = evaluateFormula(action.formula, ctx)
          if (v !== null) computed[target] = v
        }
      }
    }

    return {
      isHidden: (key: string) => hidden.has(key) && !shown.has(key),
      isRequired: (key: string) => required.has(key) && !optional.has(key),
      computed,
      loaded,
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rules, contextKey, loaded])
}
