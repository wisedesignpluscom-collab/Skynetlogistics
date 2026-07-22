import { useEffect, useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { getEntitySchema } from '../../features/config/rulesApi'
import type { CustomFieldEntityType } from '../../types/customField'
import type { ConditionOp } from '../../features/config/ruleEngine'
import type { EntityField } from '../../types/formRule'
import { WORKFLOW_EVENT_LABELS } from '../../types/workflow'
import type { Workflow, WorkflowAction, WorkflowActionType, WorkflowEvent } from '../../types/workflow'
import type { WorkflowCreatePayload, WorkflowUpdatePayload } from '../../features/config/workflowsApi'

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
const ACTION_LABELS: Record<WorkflowActionType, string> = {
  crear_alerta: 'Crear alerta',
  actualizar_campo: 'Actualizar campo (custom)',
}
const SEVERITIES = ['baja', 'media', 'alta'] as const

interface CondRow { field: string; op: ConditionOp; value: string }

const inputClass =
  'rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus:border-gold focus:outline-none'

export function WorkflowFormModal({
  entityType,
  existing,
  onClose,
  onCreate,
  onUpdate,
}: {
  entityType: CustomFieldEntityType
  existing: Workflow | null
  onClose: () => void
  onCreate: (p: WorkflowCreatePayload) => Promise<void>
  onUpdate: (id: string, p: WorkflowUpdatePayload) => Promise<void>
}) {
  const isEdit = existing !== null
  const [fields, setFields] = useState<EntityField[]>([])
  const [name, setName] = useState(existing?.name ?? '')
  const [event, setEvent] = useState<WorkflowEvent>(existing?.event ?? 'creado')
  const [match, setMatch] = useState<'all' | 'any'>(existing?.condition.match ?? 'all')
  const [rows, setRows] = useState<CondRow[]>(
    existing?.condition.conditions.map((c) => ({ field: c.field, op: c.op, value: String(c.value ?? '') })) ?? [
      { field: '', op: 'igual', value: '' },
    ]
  )
  const [actions, setActions] = useState<WorkflowAction[]>(
    existing?.actions ?? [{ type: 'crear_alerta', message: '', severity: 'media' }]
  )
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    void getEntitySchema(entityType).then((s) => setFields(s.fields))
  }, [entityType])

  const customFields = fields.filter((f) => f.source === 'custom')
  // "Estado anterior" solo tiene sentido como campo de condición cuando el evento es cambio_estado.
  const conditionFields =
    event === 'cambio_estado'
      ? [{ key: 'previous_status', label: 'Estado anterior', type: 'texto', options: [], source: 'sistema' as const }, ...fields]
      : fields

  function updateRow(i: number, patch: Partial<CondRow>) {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, ...patch } : r)))
  }
  function updateAction(i: number, patch: Partial<WorkflowAction>) {
    setActions((prev) => prev.map((a, idx) => (idx === i ? { ...a, ...patch } : a)))
  }

  async function handleSubmit() {
    if (!name.trim()) return setError('Ponle un nombre al workflow')
    const conditions = rows.filter((r) => r.field).map((r) => ({ field: r.field, op: r.op, value: r.value }))
    const cleanActions: WorkflowAction[] = actions
      .filter((a) => (a.type === 'crear_alerta' ? a.message?.trim() : a.target))
      .map((a) =>
        a.type === 'crear_alerta'
          ? { type: 'crear_alerta', message: a.message ?? '', severity: a.severity ?? 'media' }
          : { type: 'actualizar_campo', target: a.target, value: a.value ?? '' }
      )
    if (cleanActions.length === 0) return setError('Agrega al menos una acción válida')

    setIsSubmitting(true)
    setError(null)
    try {
      const condition = { match, conditions }
      if (isEdit) await onUpdate(existing.id, { name: name.trim(), condition, actions: cleanActions })
      else await onCreate({ entity_type: entityType, event, name: name.trim(), condition, actions: cleanActions })
      onClose()
    } catch {
      setError('No se pudo guardar el workflow')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={isEdit ? 'Editar workflow' : 'Nuevo workflow'} onClose={onClose}>
      <div className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto">
        <Input id="wname" label="Nombre del workflow" value={name} onChange={(e) => setName(e.target.value)} />

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="event">Cuándo</label>
          <select
            id="event"
            value={event}
            disabled={isEdit}
            onChange={(e) => setEvent(e.target.value as WorkflowEvent)}
            className={`${inputClass} disabled:opacity-60`}
          >
            {Object.entries(WORKFLOW_EVENT_LABELS).map(([ev, lbl]) => (
              <option key={ev} value={ev}>{lbl}</option>
            ))}
          </select>
          {isEdit && <span className="text-xs text-text-muted">El evento no se puede cambiar tras crear.</span>}
        </div>

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
                    {conditionFields.map((f) => (
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
          <div className="flex flex-col gap-2">
            {actions.map((a, i) => (
              <div key={i} className="flex flex-col gap-2 rounded-md border border-border p-2">
                <div className="flex items-center gap-2">
                  <select
                    value={a.type}
                    onChange={(e) => updateAction(i, { type: e.target.value as WorkflowActionType })}
                    className={inputClass}
                  >
                    {Object.entries(ACTION_LABELS).map(([t, lbl]) => (
                      <option key={t} value={t}>{lbl}</option>
                    ))}
                  </select>
                  {actions.length > 1 && (
                    <button onClick={() => setActions((p) => p.filter((_, idx) => idx !== i))} className="ml-auto text-text-muted hover:text-danger">✕</button>
                  )}
                </div>

                {a.type === 'crear_alerta' ? (
                  <div className="flex items-center gap-2">
                    <input
                      value={a.message ?? ''}
                      onChange={(e) => updateAction(i, { message: e.target.value })}
                      placeholder="Mensaje de la alerta"
                      className={`${inputClass} flex-1`}
                    />
                    <select
                      value={a.severity ?? 'media'}
                      onChange={(e) => updateAction(i, { severity: e.target.value as 'baja' | 'media' | 'alta' })}
                      className={inputClass}
                    >
                      {SEVERITIES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <select
                      value={a.target ?? ''}
                      onChange={(e) => updateAction(i, { target: e.target.value })}
                      className={`${inputClass} flex-1`}
                    >
                      <option value="">— campo custom —</option>
                      {customFields.map((f) => (
                        <option key={f.key} value={f.key}>{f.label}</option>
                      ))}
                    </select>
                    <input
                      value={String(a.value ?? '')}
                      onChange={(e) => updateAction(i, { value: e.target.value })}
                      placeholder="valor a fijar"
                      className={`${inputClass} w-32`}
                    />
                  </div>
                )}
              </div>
            ))}
            <button
              onClick={() => setActions((p) => [...p, { type: 'crear_alerta', message: '', severity: 'media' }])}
              className="self-start text-sm text-gold hover:underline"
            >
              + Agregar acción
            </button>
          </div>
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
