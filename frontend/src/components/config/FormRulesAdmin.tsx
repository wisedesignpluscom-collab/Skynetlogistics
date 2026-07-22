import { useCallback, useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { RuleFormModal } from './RuleFormModal'
import { createFormRule, deleteFormRule, listFormRules, updateFormRule } from '../../features/config/rulesApi'
import type { CustomFieldEntityType } from '../../types/customField'
import type { FormRule, FormRuleKind } from '../../types/formRule'

export function FormRulesAdmin({ entity }: { entity: CustomFieldEntityType }) {
  const [rules, setRules] = useState<FormRule[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [modalKind, setModalKind] = useState<FormRuleKind | null>(null)
  const [editing, setEditing] = useState<FormRule | null>(null)

  const reload = useCallback(async () => {
    setIsLoading(true)
    try {
      setRules(await listFormRules(entity))
    } finally {
      setIsLoading(false)
    }
  }, [entity])

  useEffect(() => {
    void reload()
  }, [reload])

  async function toggleActive(r: FormRule) {
    await updateFormRule(r.id, { active: !r.active })
    await reload()
  }
  async function remove(r: FormRule) {
    if (!window.confirm(`¿Eliminar la regla «${r.name}»?`)) return
    await deleteFormRule(r.id)
    await reload()
  }

  function openNew(kind: FormRuleKind) {
    setEditing(null)
    setModalKind(kind)
  }

  return (
    <div>
      <div className="mb-4 flex gap-3">
        <Button onClick={() => openNew('formulario')}>Nueva regla de formulario</Button>
        <Button variant="secondary" onClick={() => openNew('validacion')}>Nueva regla de validación</Button>
      </div>
      <p className="mb-4 text-sm text-text-muted">
        Las reglas de <strong>formulario</strong> muestran/ocultan/requieren o calculan campos mientras se
        llena el formulario. Las de <strong>validación</strong> bloquean el guardado si se cumple la condición.
      </p>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : rules.length === 0 ? (
        <p className="text-text-muted">Aún no hay reglas para este formulario.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Regla</th>
                <th className="px-4 py-2 font-medium">Tipo</th>
                <th className="px-4 py-2 font-medium">Condiciones</th>
                <th className="px-4 py-2 font-medium">Estado</th>
                <th className="px-4 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rules.map((r) => (
                <tr key={r.id}>
                  <td className="px-4 py-2 text-text">{r.name}</td>
                  <td className="px-4 py-2">
                    <Badge tone={r.kind === 'validacion' ? 'warning' : 'muted'}>
                      {r.kind === 'validacion' ? 'Validación' : 'Formulario'}
                    </Badge>
                  </td>
                  <td className="px-4 py-2 text-text-muted">
                    {r.condition.conditions.length === 0 ? 'Siempre' : `${r.condition.conditions.length} cond.`}
                  </td>
                  <td className="px-4 py-2">
                    {r.active ? <Badge tone="success">Activa</Badge> : <Badge tone="muted">Inactiva</Badge>}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-3 text-sm">
                      <button onClick={() => { setEditing(r); setModalKind(r.kind) }} className="text-gold hover:underline">Editar</button>
                      <button onClick={() => void toggleActive(r)} className="text-text-muted hover:text-text">
                        {r.active ? 'Desactivar' : 'Activar'}
                      </button>
                      <button onClick={() => void remove(r)} className="text-text-muted hover:text-danger">Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalKind && (
        <RuleFormModal
          entityType={entity}
          kind={modalKind}
          existing={editing}
          onClose={() => setModalKind(null)}
          onCreate={async (p) => { await createFormRule(p); await reload() }}
          onUpdate={async (id, p) => { await updateFormRule(id, p); await reload() }}
        />
      )}
    </div>
  )
}
