import { useEffect, useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { getEntitySchema } from '../../features/config/rulesApi'
import type { CustomFieldEntityType } from '../../types/customField'
import type { ConditionOp } from '../../features/config/ruleEngine'
import type {
  EntityField,
  FormActionType,
  FormRule,
  FormRuleKind,
  RuleAction,
} from '../../types/formRule'
import type { FormRuleCreatePayload, FormRuleUpdatePayload } from '../../features/config/rulesApi'

const OP_LABELS: Record<ConditionOp, string> = {
  igual: 'es igual a',
  distinto: 'es distinto de',
  mayor: 'es mayor que',
  menor: 'es menor que',
  mayor_igual: 'es mayor o igual que',
  menor_igual: 'es menor o igual que',
  en_lista: 'está en la lista (coma)',
  contiene: 'contiene',
  vacio: 'está vacío',
  no_vacio: 'no está vacío',
}
const FORM_ACTION_LABELS: Record<FormActionType, string> = {
  mostrar: 'Mostrar',
  ocultar: 'Ocultar',
  requerir: 'Requerir',
  opcional: 'Hacer opcional',
  calcular: 'Calcular (fórmula)',
}

interface CondRow { field: string; op: ConditionOp; value: string }

const inputClass =
  'rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus:border-gold focus:outline-none'

export function RuleFormModal({
  entityType,
  kind,
  existing,
  onClose,
  onCreate,
  onUpdate,
}: {
  entityType: CustomFieldEntityType
  kind: FormRuleKind
  existing: FormRule | null
  onClose: () => void
  onCreate: (p: FormRuleCreatePayload) => Promise<void>
  onUpdate: (id: string, p: FormRuleUpdatePayload) => Promise<void>
}) {
  const isEdit = existing !== null
  const [fields, setFields] = useState<EntityField[]>([])
  const [name, setName] = useState(existing?.name ?? '')
  const [match, setMatch] = useState<'all' | 'any'>(existing?.condition.match ?? 'all')
  const [rows, setRows] = useState<CondRow[]>(
    existing?.condition.conditions.map((c) => ({ field: c.field, op: c.op, value: String(c.value ?? '') })) ?? [
      { field: '', op: 'igual', value: '' },
    ]
  )
  const [actions, setActions] = useState<RuleAction[]>(
    existing?.actions ?? (kind === 'validacion' ? [{ type: 'bloquear', message: '' }] : [{ type: 'ocultar', target: '' }])
  )
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    void getEntitySchema(entityType).then((s) => setFields(s.fields))
  }, [entityType])

  function updateRow(i: number, patch: Partial<CondRow>) {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, ...patch } : r)))
  }
  function updateAction(i: number, patch: Partial<RuleAction>) {
    setActions((prev) => prev.map((a, idx) => (idx === i ? { ...a, ...patch } : a)))
  }

  async function handleSubmit() {
    if (!name.trim()) return setError('Ponle un nombre a la regla')
    const conditions = rows
      .filter((r) => r.field)
      .map((r) => ({ field: r.field, op: r.op, value: r.value }))
    const cleanActions: RuleAction[] =
      kind === 'validacion'
        ? actions.map((a) => ({ type: 'bloquear' as const, message: a.message ?? '' }))
        : actions.filter((a) => a.target).map((a) => ({
            type: a.type,
            target: a.target,
            formula: a.type === 'calcular' ? a.formula ?? '' : undefined,
          }))
    if (cleanActions.length === 0) return setError('Agrega al menos una acción')
    if (kind === 'validacion' && !cleanActions[0].message?.trim()) return setError('Escribe el mensaje de bloqueo')

    setIsSubmitting(true)
    setError(null)
    try {
      const condition = { match, conditions }
      if (isEdit) await onUpdate(existing.id, { name: name.trim(), condition, actions: cleanActions })
      else await onCreate({ entity_type: entityType, kind, name: name.trim(), condition, actions: cleanActions })
      onClose()
    } catch {
      setError('No se pudo guardar la regla')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={isEdit ? 'Editar regla' : kind === 'validacion' ? 'Nueva regla de validación' : 'Nueva regla de formulario'} onClose={onClose}>
      <div className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto">
        <Input id="rname" label="Nombre de la regla" value={name} onChange={(e) => setName(e.target.value)} />

        <div>
          <div className="mb-2 flex items-center gap-2 text-sm text-text-muted">
            <span>Si se cumplen</span>
            <select value={match} onChange={(e) => setMatch(e.target.value as 'all' | 'any')} className={inputClass}>
              <option value="all">todas</option>
              <option value="any">cualquiera</option>
            </select>
            <span>de estas condiciones:</span>
          </div>
          <div className="flex flex-col gap-2">
            {rows.map((r, i) => {
              const needsValue = r.op !== 'vacio' && r.op !== 'no_vacio'
              return (
                <div key={i} className="flex items-center gap-2">
                  <select value={r.field} onChange={(e) => updateRow(i, { field: e.target.value })} className={`${inputClass} flex-1`}>
                    <option value="">— campo —</option>
                    {fields.map((f) => (
                      <option key={f.key} value={f.key}>{f.label}{f.source === 'custom' ? ' (custom)' : ''}</option>
                    ))}
                  </select>
                  <select value={r.op} onChange={(e) => updateRow(i, { op: e.target.value as ConditionOp })} className={inputClass}>
                    {Object.entries(OP_LABELS).map(([op, lbl]) => (
                      <option key={op} value={op}>{lbl}</option>
                    ))}
                  </select>
                  {needsValue && (
                    <input value={r.value} onChange={(e) => updateRow(i, { value: e.target.value })} placeholder="valor" className={`${inputClass} w-28`} />
                  )}
                  {rows.length > 1 && (
                    <button onClick={() => setRows((p) => p.filter((_, idx) => idx !== i))} className="text-text-muted hover:text-danger">✕</button>
                  )}
                </div>
              )
            })}
            <button onClick={() => setRows((p) => [...p, { field: '', op: 'igual', value: '' }])} className="self-start text-sm text-gold hover:underline">
              + Agregar condición
            </button>
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm text-text-muted">Entonces:</p>
          {kind === 'validacion' ? (
            <Input id="msg" label="Bloquear con el mensaje" value={actions[0]?.message ?? ''} onChange={(e) => updateAction(0, { message: e.target.value })} />
          ) : (
            <div className="flex flex-col gap-2">
              {actions.map((a, i) => (
                <div key={i} className="flex items-center gap-2">
                  <select value={a.type} onChange={(e) => updateAction(i, { type: e.target.value as FormActionType })} className={inputClass}>
                    {Object.entries(FORM_ACTION_LABELS).map(([t, lbl]) => (
                      <option key={t} value={t}>{lbl}</option>
                    ))}
                  </select>
                  <select value={a.target ?? ''} onChange={(e) => updateAction(i, { target: e.target.value })} className={`${inputClass} flex-1`}>
                    <option value="">— campo —</option>
                    {fields.map((f) => (
                      <option key={f.key} value={f.key}>{f.label}{f.source === 'custom' ? ' (custom)' : ''}</option>
                    ))}
                  </select>
                  {a.type === 'calcular' && (
                    <input value={a.formula ?? ''} onChange={(e) => updateAction(i, { formula: e.target.value })} placeholder="ej. campoA * 2" className={`${inputClass} w-32`} />
                  )}
                  {actions.length > 1 && (
                    <button onClick={() => setActions((p) => p.filter((_, idx) => idx !== i))} className="text-text-muted hover:text-danger">✕</button>
                  )}
                </div>
              ))}
              <button onClick={() => setActions((p) => [...p, { type: 'ocultar', target: '' }])} className="self-start text-sm text-gold hover:underline">
                + Agregar acción
              </button>
            </div>
          )}
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancelar</Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>{isSubmitting ? 'Guardando…' : 'Guardar'}</Button>
        </div>
      </div>
    </Modal>
  )
}
