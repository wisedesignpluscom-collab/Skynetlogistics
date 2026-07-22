import { useState } from 'react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { CustomFieldFormModal } from './CustomFieldFormModal'
import { useCustomFields } from '../../features/config/hooks'
import { createCustomField, deleteCustomField, updateCustomField } from '../../features/config/api'
import { CUSTOM_FIELD_TYPE_LABELS } from '../../types/customField'
import type { CustomFieldDefinition, CustomFieldEntityType } from '../../types/customField'

export function CustomFieldsAdmin({ entity }: { entity: CustomFieldEntityType }) {
  const { fields, isLoading, reload } = useCustomFields(entity, false)
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<CustomFieldDefinition | null>(null)

  async function toggleActive(f: CustomFieldDefinition) {
    await updateCustomField(f.id, { active: !f.active })
    await reload()
  }
  async function remove(f: CustomFieldDefinition) {
    if (!window.confirm(`¿Eliminar el campo «${f.label}»? Los datos ya guardados no se borran.`)) return
    await deleteCustomField(f.id)
    await reload()
  }

  return (
    <div>
      <div className="mb-4">
        <Button onClick={() => { setEditing(null); setShowModal(true) }}>Nuevo campo</Button>
      </div>

      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : fields.length === 0 ? (
        <p className="text-text-muted">Aún no hay campos personalizados para este formulario.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Campo</th>
                <th className="px-4 py-2 font-medium">Clave</th>
                <th className="px-4 py-2 font-medium">Tipo</th>
                <th className="px-4 py-2 font-medium">Obligatorio</th>
                <th className="px-4 py-2 font-medium">Estado</th>
                <th className="px-4 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {fields.map((f) => (
                <tr key={f.id}>
                  <td className="px-4 py-2 text-text">{f.label}</td>
                  <td className="px-4 py-2 font-mono text-xs text-text-muted">{f.key}</td>
                  <td className="px-4 py-2 text-text-muted">
                    {CUSTOM_FIELD_TYPE_LABELS[f.field_type]}
                    {f.field_type === 'select' && ` (${f.options.length})`}
                  </td>
                  <td className="px-4 py-2 text-text-muted">{f.required ? 'Sí' : 'No'}</td>
                  <td className="px-4 py-2">
                    {f.active ? <Badge tone="success">Activo</Badge> : <Badge tone="muted">Inactivo</Badge>}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-3 text-sm">
                      <button onClick={() => { setEditing(f); setShowModal(true) }} className="text-gold hover:underline">Editar</button>
                      <button onClick={() => void toggleActive(f)} className="text-text-muted hover:text-text">
                        {f.active ? 'Desactivar' : 'Activar'}
                      </button>
                      <button onClick={() => void remove(f)} className="text-text-muted hover:text-danger">Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <CustomFieldFormModal
          entityType={entity}
          existing={editing}
          onClose={() => setShowModal(false)}
          onCreate={async (payload) => { await createCustomField(payload); await reload() }}
          onUpdate={async (id, payload) => { await updateCustomField(id, payload); await reload() }}
        />
      )}
    </div>
  )
}
