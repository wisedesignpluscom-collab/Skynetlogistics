import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Input } from '../components/ui/Input'
import { TripExpenseSection } from '../components/trips/TripExpenseSection'
import { TripCloseModal } from '../components/trips/TripCloseModal'
import {
  cancelTrip,
  createTripExpense,
  deleteTripExpense,
  getTrip,
  setTripAdvance,
  startTrip,
  closeTrip,
} from '../features/trips/api'
import { useAuth } from '../features/auth/AuthContext'
import type { TripWithDetails } from '../types/trip'

const statusTone = {
  planificado: 'muted',
  en_curso: 'gold',
  completado: 'gold',
  cancelado: 'danger',
} as const

export function TripDetailPage() {
  const { tripId } = useParams<{ tripId: string }>()
  const { hasPermission } = useAuth()
  const [trip, setTrip] = useState<TripWithDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [startOdometerKm, setStartOdometerKm] = useState('')
  const [advanceAmount, setAdvanceAmount] = useState('')
  const [showCloseModal, setShowCloseModal] = useState(false)

  const canWrite = hasPermission('trips', 'write')

  const reload = useCallback(async () => {
    if (!tripId) return
    setIsLoading(true)
    setTrip(await getTrip(tripId))
    setIsLoading(false)
  }, [tripId])

  useEffect(() => {
    void reload()
  }, [reload])

  if (isLoading || !trip) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  async function handleStart() {
    await startTrip(trip!.id, Number(startOdometerKm))
    await reload()
  }

  async function handleAdvance() {
    await setTripAdvance(trip!.id, Number(advanceAmount))
    setAdvanceAmount('')
    await reload()
  }

  async function handleCancel() {
    if (!window.confirm('¿Cancelar este viaje?')) return
    await cancelTrip(trip!.id)
    await reload()
  }

  return (
    <DashboardLayout>
      <Link to="/trips" className="text-sm text-text-muted hover:text-gold">
        ← Volver a viajes
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">
            {trip.origin} → {trip.destination}
          </h1>
          <p className="text-text-muted">
            {trip.cargo_type} · {trip.distance_km !== null ? `${trip.distance_km} km` : 'distancia sin estimar'}
          </p>
        </div>
        <Badge tone={statusTone[trip.status]}>{trip.status}</Badge>
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        <a
          href={`/api/v1/trips/${trip.id}/documents/loading-order`}
          target="_blank"
          rel="noreferrer"
          className="text-sm text-text-muted hover:text-gold"
        >
          Orden de carga (imprimir)
        </a>
        <a
          href={`/api/v1/trips/${trip.id}/documents/expense-receipt`}
          target="_blank"
          rel="noreferrer"
          className="text-sm text-text-muted hover:text-gold"
        >
          Recibo de viáticos (imprimir)
        </a>
        <Link to={`/trips/${trip.id}/route`} className="text-sm text-text-muted hover:text-gold">
          Ruta planeada
        </Link>
      </div>

      {canWrite && trip.status === 'planificado' && (
        <div className="mb-6 flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <Input
            id="start_odometer"
            label="Odómetro de inicio (km)"
            type="number"
            value={startOdometerKm}
            onChange={(e) => setStartOdometerKm(e.target.value)}
          />
          <Button onClick={handleStart} disabled={!startOdometerKm}>
            Iniciar viaje
          </Button>
          <Button variant="secondary" onClick={handleCancel}>
            Cancelar viaje
          </Button>
        </div>
      )}

      {canWrite && trip.status === 'en_curso' && (
        <div className="mb-6 flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <Input
            id="advance_amount"
            label="Anticipo acumulado ($)"
            type="number"
            min={0}
            step="0.01"
            value={advanceAmount || trip.advance_payment.toString()}
            onChange={(e) => setAdvanceAmount(e.target.value)}
          />
          <Button variant="secondary" onClick={handleAdvance}>
            Actualizar anticipo
          </Button>
          <Button onClick={() => setShowCloseModal(true)}>Cerrar viaje</Button>
          <Button variant="secondary" onClick={handleCancel}>
            Cancelar viaje
          </Button>
        </div>
      )}

      {trip.payroll && (
        <div className="mb-6 rounded-lg border border-border bg-surface p-4 text-sm">
          <p className="mb-2 font-display text-text">Nómina del viaje</p>
          <dl className="grid grid-cols-2 gap-y-1 text-text-muted">
            <dt>Salario base</dt>
            <dd className="text-right text-text">${trip.payroll.base_salary.toFixed(2)}</dd>
            <dt>Bonos (alimentación + feriados + retorno)</dt>
            <dd className="text-right text-text">${trip.payroll.bonuses.toFixed(2)}</dd>
            <dt>Anticipo</dt>
            <dd className="text-right text-text">-${trip.payroll.advance_payment.toFixed(2)}</dd>
            <dt className="font-medium text-text">Total a pagar</dt>
            <dd className="text-right font-medium text-gold">${trip.payroll.total_to_pay.toFixed(2)}</dd>
          </dl>
        </div>
      )}

      <h2 className="mb-3 font-display text-lg text-text">Gastos del viaje</h2>
      <TripExpenseSection
        expenses={trip.expenses}
        canAdd={canWrite && trip.status === 'en_curso'}
        onAdd={async (values) => {
          await createTripExpense(trip.id, values)
          await reload()
        }}
        onDelete={async (expense) => {
          await deleteTripExpense(trip.id, expense.id)
          await reload()
        }}
      />

      {showCloseModal && (
        <TripCloseModal
          trip={trip}
          onClose={() => setShowCloseModal(false)}
          onSubmit={async (values) => {
            await closeTrip(trip.id, values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
