import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useProviders } from '../../features/providers/hooks'
import type { CompleteTaskPayload } from '../../features/maintenance/api'

interface CompleteTaskModalProps {
  onClose: () => void
  onSubmit: (values: CompleteTaskPayload) => Promise<void>
}

export function CompleteTaskModal({ onClose, onSubmit }: CompleteTaskModalProps) {
  const { providers } = useProviders()
  const [costLabor, setCostLabor] = useState('0')
  const [costParts, setCostParts] = useState('0')
  const [providerId, setProviderId] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        cost_labor: Number(costLabor),
        cost_parts: Number(costParts),
        provider_id: providerId || null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo completar la tarea')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Completar mantenimiento" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <Input
            id="cost_labor"
            label="Mano de obra"
            type="number"
            min={0}
            step="0.01"
            value={costLabor}
            onChange={(e) => setCostLabor(e.target.value)}
          />
          <Input
            id="cost_parts"
            label="Repuestos"
            type="number"
            min={0}
            step="0.01"
            value={costParts}
            onChange={(e) => setCostParts(e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="provider">
            Proveedor
          </label>
          <select
            id="provider"
            value={providerId}
            onChange={(e) => setProviderId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Sin especificar</option>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="notes">
            Notas
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>
        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Completar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
