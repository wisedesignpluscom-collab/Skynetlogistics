import { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { createIncidentReport } from '../../features/incidents/api'
import { INCIDENT_SEVERITY_LABELS, INCIDENT_TYPE_LABELS } from '../../types/incident'
import type { IncidentSeverity, IncidentType } from '../../types/incident'

const TYPE_OPTIONS = Object.entries(INCIDENT_TYPE_LABELS) as [IncidentType, string][]
const SEVERITY_OPTIONS = Object.entries(INCIDENT_SEVERITY_LABELS) as [IncidentSeverity, string][]

export function IncidentReportFormModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: () => void
}) {
  const [type, setType] = useState<IncidentType>('averia_mecanica')
  const [severity, setSeverity] = useState<IncidentSeverity>('media')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit() {
    if (!description.trim()) {
      setError('Describe brevemente lo ocurrido')
      return
    }
    setIsSubmitting(true)
    setError(null)
    try {
      await createIncidentReport({ type, severity, description: description.trim() })
      onCreated()
      onClose()
    } catch {
      setError('No se pudo enviar el reporte, intenta de nuevo')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Reportar incidencia" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="incident-type">
            Tipo de incidencia
          </label>
          <select
            id="incident-type"
            value={type}
            onChange={(e) => setType(e.target.value as IncidentType)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {TYPE_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="incident-severity">
            Urgencia
          </label>
          <select
            id="incident-severity"
            value={severity}
            onChange={(e) => setSeverity(e.target.value as IncidentSeverity)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {SEVERITY_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="incident-description">
            ¿Qué pasó?
          </label>
          <textarea
            id="incident-description"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text placeholder:text-text-muted/60 focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            placeholder="Describe brevemente lo ocurrido…"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>
            {isSubmitting ? 'Enviando…' : 'Enviar reporte'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
