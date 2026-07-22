import { useEffect } from 'react'
import { Input } from '../ui/Input'
import { useCustomFields } from '../../features/config/hooks'
import { useFormRules, type FormRulesResult } from '../../features/config/useFormRules'
import type { CustomData, CustomFieldEntityType } from '../../types/customField'

/** Renderiza dinámicamente los campos custom activos de una entidad (Config-A) y aplica en vivo las
 *  reglas de formulario de Config-B (mostrar/ocultar/requerir/calcular). `systemValues` son los
 *  valores de los campos base del formulario host, para que las condiciones puedan leerlos.
 *  Si el formulario host ya evaluó las reglas para sus propios campos de sistema (vía
 *  `useSystemFieldRules`), se le pasa por `rules` para no recargar/reevaluar dos veces. */
export function CustomFieldsSection({
  entityType,
  value,
  onChange,
  systemValues = {},
  rules: externalRules,
}: {
  entityType: CustomFieldEntityType
  value: CustomData
  onChange: (next: CustomData) => void
  systemValues?: Record<string, unknown>
  rules?: FormRulesResult
}) {
  const { fields, isLoading } = useCustomFields(entityType, true)

  // Contexto de evaluación: campos de sistema + custom aplanados como `custom.<key>`.
  const context: Record<string, unknown> = { ...systemValues }
  for (const [k, v] of Object.entries(value)) context[`custom.${k}`] = v
  // Hook siempre invocado (regla de hooks); si ya vino `rules` externo, se le pasa entityType
  // undefined para que no dispare su propia carga — se descarta el resultado interno.
  const internalRules = useFormRules(externalRules ? undefined : entityType, context)
  const rules = externalRules ?? internalRules

  // Autocompletar campos calculados.
  useEffect(() => {
    for (const [target, computedVal] of Object.entries(rules.computed)) {
      if (!target.startsWith('custom.')) continue
      const key = target.slice('custom.'.length)
      if (value[key] !== computedVal) onChange({ ...value, [key]: computedVal })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(rules.computed)])

  if (isLoading || fields.length === 0) return null

  const visibleFields = fields.filter((f) => !rules.isHidden(`custom.${f.key}`))
  if (visibleFields.length === 0) return null

  function setField(key: string, v: unknown) {
    onChange({ ...value, [key]: v })
  }

  return (
    <div className="flex flex-col gap-4 border-t border-border pt-4">
      <p className="text-sm font-medium text-text-muted">Campos adicionales</p>
      {visibleFields.map((f) => {
        const current = value[f.key]
        const ruleRequired = rules.isRequired(`custom.${f.key}`)
        const label = f.required || ruleRequired ? `${f.label} *` : f.label

        if (f.field_type === 'select') {
          return (
            <div key={f.id} className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor={`cf_${f.key}`}>{label}</label>
              <select
                id={`cf_${f.key}`}
                value={(current as string) ?? ''}
                onChange={(e) => setField(f.key, e.target.value)}
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                <option value="">—</option>
                {f.options.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
              {f.help_text && <span className="text-xs text-text-muted">{f.help_text}</span>}
            </div>
          )
        }

        if (f.field_type === 'checkbox') {
          return (
            <label key={f.id} className="flex items-center gap-2 text-sm text-text">
              <input type="checkbox" checked={Boolean(current)} onChange={(e) => setField(f.key, e.target.checked)} />
              {label}
            </label>
          )
        }

        if (f.field_type === 'area_texto') {
          return (
            <div key={f.id} className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor={`cf_${f.key}`}>{label}</label>
              <textarea
                id={`cf_${f.key}`}
                rows={2}
                value={(current as string) ?? ''}
                onChange={(e) => setField(f.key, e.target.value)}
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              />
              {f.help_text && <span className="text-xs text-text-muted">{f.help_text}</span>}
            </div>
          )
        }

        const inputType = f.field_type === 'numero' ? 'number' : f.field_type === 'fecha' ? 'date' : 'text'
        return (
          <Input
            key={f.id}
            id={`cf_${f.key}`}
            label={label}
            type={inputType}
            step={f.field_type === 'numero' ? 'any' : undefined}
            value={(current as string | number) ?? ''}
            onChange={(e) => setField(f.key, e.target.value)}
          />
        )
      })}
    </div>
  )
}
