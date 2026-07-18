import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { useFatigueRules } from '../features/fatigue/hooks'
import { updateFatigueRules } from '../features/fatigue/api'
import { useAuth } from '../features/auth/AuthContext'

export function FatigueSettingsPage() {
  const { hasPermission } = useAuth()
  const { rule, isLoading, reload } = useFatigueRules()
  const canWrite = hasPermission('fatigue', 'write')

  const [maxContinuous, setMaxContinuous] = useState('')
  const [max24h, setMax24h] = useState('')
  const [max7day, setMax7day] = useState('')
  const [nightWeight, setNightWeight] = useState('')
  const [nightStart, setNightStart] = useState('')
  const [nightEnd, setNightEnd] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (!rule) return
    setMaxContinuous(String(rule.max_continuous_hours))
    setMax24h(String(rule.max_24h_hours))
    setMax7day(String(rule.max_7day_hours))
    setNightWeight(String(rule.night_driving_weight))
    setNightStart(String(rule.night_start_hour))
    setNightEnd(String(rule.night_end_hour))
  }, [rule])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setIsSubmitting(true)
    try {
      await updateFatigueRules({
        max_continuous_hours: Number(maxContinuous),
        max_24h_hours: Number(max24h),
        max_7day_hours: Number(max7day),
        night_driving_weight: Number(nightWeight),
        night_start_hour: Number(nightStart),
        night_end_hour: Number(nightEnd),
      })
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
      <Link to="/drivers" className="text-sm text-text-muted hover:text-gold">
        ← Volver a conductores
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="font-display text-2xl text-text">Reglas de fatiga</h1>
        <p className="text-sm text-text-muted">
          Umbrales de horas de servicio usados para calcular el riesgo de fatiga de cada conductor.
        </p>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      {rule && (
        <form
          onSubmit={handleSubmit}
          className="flex max-w-xl flex-col gap-4 rounded-lg border border-border p-4"
        >
          <Input
            id="max_continuous_hours"
            label="Máximo de horas continuas manejando"
            type="number"
            min={0.5}
            max={24}
            step="0.5"
            value={maxContinuous}
            onChange={(e) => setMaxContinuous(e.target.value)}
            disabled={!canWrite}
            required
          />
          <Input
            id="max_24h_hours"
            label="Máximo de horas manejadas en 24h"
            type="number"
            min={0.5}
            max={24}
            step="0.5"
            value={max24h}
            onChange={(e) => setMax24h(e.target.value)}
            disabled={!canWrite}
            required
          />
          <Input
            id="max_7day_hours"
            label="Máximo de horas manejadas en 7 días"
            type="number"
            min={1}
            max={168}
            step="0.5"
            value={max7day}
            onChange={(e) => setMax7day(e.target.value)}
            disabled={!canWrite}
            required
          />
          <Input
            id="night_driving_weight"
            label="Peso de manejo nocturno (multiplicador de riesgo)"
            type="number"
            min={1}
            max={5}
            step="0.1"
            value={nightWeight}
            onChange={(e) => setNightWeight(e.target.value)}
            disabled={!canWrite}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              id="night_start_hour"
              label="Inicio de horario nocturno (hora, 0-23)"
              type="number"
              min={0}
              max={23}
              value={nightStart}
              onChange={(e) => setNightStart(e.target.value)}
              disabled={!canWrite}
              required
            />
            <Input
              id="night_end_hour"
              label="Fin de horario nocturno (hora, 0-23)"
              type="number"
              min={0}
              max={23}
              value={nightEnd}
              onChange={(e) => setNightEnd(e.target.value)}
              disabled={!canWrite}
              required
            />
          </div>

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
