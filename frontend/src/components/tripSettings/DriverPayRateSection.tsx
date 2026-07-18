import { useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useDriverPayRates } from '../../features/tripSettings/hooks'
import { createDriverPayRate, deleteDriverPayRate } from '../../features/tripSettings/api'
import type { VehicleType } from '../../types/vehicle'

const VEHICLE_TYPES: VehicleType[] = ['camion', 'remolque', 'cabezal']

export function DriverPayRateSection({ canWrite }: { canWrite: boolean }) {
  const { rates, isLoading, reload } = useDriverPayRates()
  const [vehicleType, setVehicleType] = useState<VehicleType>('camion')
  const [dailyBaseRate, setDailyBaseRate] = useState('')
  const [mealAllowance, setMealAllowance] = useState('0')
  const [holidayBonus, setHolidayBonus] = useState('0')
  const [returnBonus, setReturnBonus] = useState('0')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await createDriverPayRate({
        vehicle_type: vehicleType,
        daily_base_rate: Number(dailyBaseRate),
        meal_allowance_per_day: Number(mealAllowance),
        holiday_bonus_rate: Number(holidayBonus),
        return_bonus_rate: Number(returnBonus),
      })
      setDailyBaseRate('')
      setMealAllowance('0')
      setHolidayBonus('0')
      setReturnBonus('0')
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('¿Eliminar este tabulado de pago?')) return
    await deleteDriverPayRate(id)
    await reload()
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Tipo de unidad</th>
              <th className="px-4 py-2 font-medium">Base/día</th>
              <th className="px-4 py-2 font-medium">Alimentación/día</th>
              <th className="px-4 py-2 font-medium">Bono feriado</th>
              <th className="px-4 py-2 font-medium">Bono retorno</th>
              {canWrite && <th className="px-4 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rates.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-2">{r.vehicle_type}</td>
                <td className="px-4 py-2 text-text-muted">${r.daily_base_rate}</td>
                <td className="px-4 py-2 text-text-muted">${r.meal_allowance_per_day}</td>
                <td className="px-4 py-2 text-text-muted">${r.holiday_bonus_rate}</td>
                <td className="px-4 py-2 text-text-muted">${r.return_bonus_rate}</td>
                {canWrite && (
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => handleDelete(r.id)} className="text-text-muted hover:text-danger">
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {!isLoading && rates.length === 0 && (
              <tr>
                <td colSpan={canWrite ? 6 : 5} className="px-4 py-6 text-center text-text-muted">
                  No hay tabulados de pago configurados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {canWrite && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="dpr_vehicle_type">
              Tipo de unidad
            </label>
            <select
              id="dpr_vehicle_type"
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value as VehicleType)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              {VEHICLE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <Input
            id="dpr_base"
            label="Base/día ($)"
            type="number"
            min={0}
            step="0.01"
            value={dailyBaseRate}
            onChange={(e) => setDailyBaseRate(e.target.value)}
            required
          />
          <Input
            id="dpr_meal"
            label="Alimentación/día ($)"
            type="number"
            min={0}
            step="0.01"
            value={mealAllowance}
            onChange={(e) => setMealAllowance(e.target.value)}
          />
          <Input
            id="dpr_holiday"
            label="Bono feriado ($)"
            type="number"
            min={0}
            step="0.01"
            value={holidayBonus}
            onChange={(e) => setHolidayBonus(e.target.value)}
          />
          <Input
            id="dpr_return"
            label="Bono retorno ($)"
            type="number"
            min={0}
            step="0.01"
            value={returnBonus}
            onChange={(e) => setReturnBonus(e.target.value)}
          />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Agregar'}
          </Button>
        </form>
      )}
    </div>
  )
}
