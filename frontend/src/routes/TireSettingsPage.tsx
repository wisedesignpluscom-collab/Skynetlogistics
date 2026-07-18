import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { useTireSettings } from '../features/tires/hooks'
import { updateTireSettings } from '../features/tires/api'
import { useAuth } from '../features/auth/AuthContext'

export function TireSettingsPage() {
  const { hasPermission } = useAuth()
  const { settings, isLoading, reload } = useTireSettings()
  const canWrite = hasPermission('tires', 'write')

  const [threshold, setThreshold] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (settings) setThreshold(String(settings.disparity_threshold_mm))
  }, [settings])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setIsSubmitting(true)
    try {
      await updateTireSettings(Number(threshold))
      await reload()
      setSaved(true)
    } catch {
      setError('No se pudo guardar la configuración')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <DashboardLayout>
      <Link to="/tires" className="text-sm text-text-muted hover:text-gold">
        ← Volver a neumáticos
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="font-display text-2xl text-text">Umbral de disparidad</h1>
        <p className="text-sm text-text-muted">
          Diferencia de espesor (mm) entre neumáticos del mismo eje ("morocha") a partir de la
          cual se genera una alerta.
        </p>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      {settings && (
        <form onSubmit={handleSubmit} className="flex max-w-md flex-col gap-4 rounded-lg border border-border p-4">
          <Input
            id="disparity_threshold_mm"
            label="Umbral de disparidad (mm)"
            type="number"
            min={0.1}
            max={20}
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            disabled={!canWrite}
            required
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          {saved && <p className="text-sm text-gold">Configuración guardada.</p>}
          {canWrite && (
            <div className="flex justify-end">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Guardando…' : 'Guardar'}
              </Button>
            </div>
          )}
        </form>
      )}
    </DashboardLayout>
  )
}
