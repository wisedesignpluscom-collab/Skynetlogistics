import { useEffect, useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { getMaintenanceSettings } from '../../features/maintenance/api'
import type { MaintenanceSettingsPayload } from '../../features/maintenance/api'

interface MaintenanceSettingsModalProps {
  onClose: () => void
  onSubmit: (values: MaintenanceSettingsPayload) => Promise<void>
}

export function MaintenanceSettingsModal({ onClose, onSubmit }: MaintenanceSettingsModalProps) {
  const [warningDays, setWarningDays] = useState('')
  const [warningKm, setWarningKm] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    void getMaintenanceSettings().then((settings) => {
      setWarningDays(String(settings.warning_days_threshold))
      setWarningKm(String(settings.warning_km_threshold))
      setIsLoading(false)
    })
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        warning_days_threshold: Number(warningDays),
        warning_km_threshold: Number(warningKm),
      })
      onClose()
    } catch {
      setError('No se pudo guardar la configuración')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Configurar semáforo de mantenimiento" onClose={onClose}>
      {isLoading ? (
        <p className="text-text-muted">Cargando…</p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            id="warning_days_threshold"
            label="Días de aviso antes del vencimiento (tareas por fecha)"
            type="number"
            min={0}
            value={warningDays}
            onChange={(e) => setWarningDays(e.target.value)}
            required
          />
          <Input
            id="warning_km_threshold"
            label="Kilómetros de aviso antes del vencimiento (tareas por km)"
            type="number"
            min={0}
            value={warningKm}
            onChange={(e) => setWarningKm(e.target.value)}
            required
          />
          <p className="text-sm text-text-muted">
            Dentro de este umbral la tarea se muestra en amarillo; al alcanzar o superar la fecha/km límite se
            muestra en rojo.
          </p>

          {error && <p className="text-sm text-danger">{error}</p>}
          <div className="mt-2 flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Guardando…' : 'Guardar'}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  )
}
