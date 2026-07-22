import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import type { MaintenanceType, ScheduledBy } from '../../types/maintenance'
import type { MaintenanceTaskPayload } from '../../features/maintenance/api'
import type { CustomData } from '../../types/customField'

interface MaintenanceTaskFormModalProps {
  vehicleId: string
  onClose: () => void
  onSubmit: (values: MaintenanceTaskPayload) => Promise<void>
}

export function MaintenanceTaskFormModal({ vehicleId, onClose, onSubmit }: MaintenanceTaskFormModalProps) {
  const [type, setType] = useState<MaintenanceType>('preventivo')
  const [scheduledBy, setScheduledBy] = useState<ScheduledBy>('tiempo')
  const [dueDate, setDueDate] = useState('')
  const [dueKm, setDueKm] = useState('')
  const [description, setDescription] = useState('')
  const [customData, setCustomData] = useState<CustomData>({})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules('maintenance_task', { type, scheduled_by: scheduledBy, due_km: dueKm }, customData)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        vehicle_id: vehicleId,
        type,
        scheduled_by: scheduledBy,
        due_date: scheduledBy === 'tiempo' ? dueDate : null,
        due_km: scheduledBy === 'km' ? Number(dueKm) : null,
        description: description || null,
        custom_data: customData,
      })
      onClose()
    } catch {
      setError('No se pudo programar la tarea')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Programar mantenimiento" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {!rules.isHidden('type') && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="type">
              {rules.isRequired('type') ? 'Tipo *' : 'Tipo'}
            </label>
            <select
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value as MaintenanceType)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              <option value="preventivo">Preventivo</option>
              <option value="correctivo">Correctivo</option>
            </select>
          </div>
        )}

        {!rules.isHidden('scheduled_by') && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="scheduled_by">
              {rules.isRequired('scheduled_by') ? 'Programado por *' : 'Programado por'}
            </label>
            <select
              id="scheduled_by"
              value={scheduledBy}
              onChange={(e) => setScheduledBy(e.target.value as ScheduledBy)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              <option value="tiempo">Fecha</option>
              <option value="km">Kilometraje</option>
            </select>
          </div>
        )}

        {scheduledBy === 'tiempo' ? (
          <Input
            id="due_date"
            label="Fecha límite"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            required
          />
        ) : (
          !rules.isHidden('due_km') && (
            <Input
              id="due_km"
              label={rules.isRequired('due_km') ? 'Kilometraje límite *' : 'Kilometraje límite'}
              type="number"
              min={0}
              value={dueKm}
              onChange={(e) => setDueKm(e.target.value)}
              required
            />
          )
        )}

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="description">
            Descripción
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>

        <CustomFieldsSection
          entityType="maintenance_task"
          value={customData}
          onChange={setCustomData}
          systemValues={{ type, scheduled_by: scheduledBy, due_km: dueKm }}
          rules={rules}
        />

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Programar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
