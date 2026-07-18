import { useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useHolidays } from '../../features/tripSettings/hooks'
import { createHoliday, deleteHoliday } from '../../features/tripSettings/api'

export function HolidaySection({ canWrite }: { canWrite: boolean }) {
  const { holidays, isLoading, reload } = useHolidays()
  const [date, setDate] = useState('')
  const [name, setName] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await createHoliday({ date, name })
      setDate('')
      setName('')
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('¿Eliminar este feriado?')) return
    await deleteHoliday(id)
    await reload()
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Fecha</th>
              <th className="px-4 py-2 font-medium">Nombre</th>
              {canWrite && <th className="px-4 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {holidays.map((h) => (
              <tr key={h.id}>
                <td className="px-4 py-2">{h.date}</td>
                <td className="px-4 py-2 text-text-muted">{h.name}</td>
                {canWrite && (
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => handleDelete(h.id)} className="text-text-muted hover:text-danger">
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {!isLoading && holidays.length === 0 && (
              <tr>
                <td colSpan={canWrite ? 3 : 2} className="px-4 py-6 text-center text-text-muted">
                  No hay feriados registrados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {canWrite && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <Input id="holiday_date" label="Fecha" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          <Input id="holiday_name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Agregar'}
          </Button>
        </form>
      )}
    </div>
  )
}
