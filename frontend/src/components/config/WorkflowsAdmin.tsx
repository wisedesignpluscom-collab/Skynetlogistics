import { useCallback, useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { WorkflowFormModal } from './WorkflowFormModal'
import { createWorkflow, deleteWorkflow, listWorkflows, updateWorkflow } from '../../features/config/workflowsApi'
import { WORKFLOW_EVENT_LABELS } from '../../types/workflow'
import type { CustomFieldEntityType } from '../../types/customField'
import type { Workflow } from '../../types/workflow'

export function WorkflowsAdmin({ entity }: { entity: CustomFieldEntityType }) {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Workflow | null>(null)

  const reload = useCallback(async () => {
    setIsLoading(true)
    try {
      setWorkflows(await listWorkflows(entity))
    } finally {
      setIsLoading(false)
    }
  }, [entity])

  useEffect(() => {
    void reload()
  }, [reload])

  async function toggleActive(w: Workflow) {
    await updateWorkflow(w.id, { active: !w.active })
    await reload()
  }
  async function remove(w: Workflow) {
    if (!window.confirm(`¿Eliminar el workflow «${w.name}»?`)) return
    await deleteWorkflow(w.id)
    await reload()
  }

  return (
    <div>
      <div className="mb-4">
        <Button onClick={() => { setEditing(null); setShowModal(true) }}>Nuevo workflow</Button>
      </div>
      <p className="mb-4 text-sm text-text-muted">
        Los workflows corren automáticamente <strong>después</strong> de guardar: si la condición se
        cumple, ejecutan sus acciones (crear una alerta o fijar un campo personalizado) sin
        intervención manual.
      </p>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : workflows.length === 0 ? (
        <p className="text-text-muted">Aún no hay workflows para este formulario.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Workflow</th>
                <th className="px-4 py-2 font-medium">Cuándo</th>
                <th className="px-4 py-2 font-medium">Condiciones</th>
                <th className="px-4 py-2 font-medium">Acciones</th>
                <th className="px-4 py-2 font-medium">Estado</th>
                <th className="px-4 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {workflows.map((w) => (
                <tr key={w.id}>
                  <td className="px-4 py-2 text-text">{w.name}</td>
                  <td className="px-4 py-2 text-text-muted">{WORKFLOW_EVENT_LABELS[w.event]}</td>
                  <td className="px-4 py-2 text-text-muted">
                    {w.condition.conditions.length === 0 ? 'Siempre' : `${w.condition.conditions.length} cond.`}
                  </td>
                  <td className="px-4 py-2 text-text-muted">{w.actions.length}</td>
                  <td className="px-4 py-2">
                    {w.active ? <Badge tone="success">Activo</Badge> : <Badge tone="muted">Inactivo</Badge>}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-3 text-sm">
                      <button onClick={() => { setEditing(w); setShowModal(true) }} className="text-gold hover:underline">Editar</button>
                      <button onClick={() => void toggleActive(w)} className="text-text-muted hover:text-text">
                        {w.active ? 'Desactivar' : 'Activar'}
                      </button>
                      <button onClick={() => void remove(w)} className="text-text-muted hover:text-danger">Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <WorkflowFormModal
          entityType={entity}
          existing={editing}
          onClose={() => setShowModal(false)}
          onCreate={async (p) => { await createWorkflow(p); await reload() }}
          onUpdate={async (id, p) => { await updateWorkflow(id, p); await reload() }}
        />
      )}
    </div>
  )
}
