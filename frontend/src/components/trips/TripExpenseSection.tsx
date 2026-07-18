import { useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useExpenseConcepts } from '../../features/tripSettings/hooks'
import type { TripExpense } from '../../types/trip'

interface TripExpenseSectionProps {
  expenses: TripExpense[]
  canAdd: boolean
  onAdd: (values: { concept_id: string; amount: number; notes?: string | null }) => Promise<void>
  onDelete: (expense: TripExpense) => void
}

export function TripExpenseSection({ expenses, canAdd, onAdd, onDelete }: TripExpenseSectionProps) {
  const { concepts } = useExpenseConcepts()
  const [conceptId, setConceptId] = useState('')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const total = expenses.reduce((sum, e) => sum + e.amount, 0)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onAdd({ concept_id: conceptId, amount: Number(amount), notes: notes || null })
      setConceptId('')
      setAmount('')
      setNotes('')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-2 font-medium">Concepto</th>
            <th className="px-4 py-2 font-medium">Notas</th>
            <th className="px-4 py-2 font-medium">Monto</th>
            {canAdd && <th className="px-4 py-2" />}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td className="px-4 py-2">{concepts.find((c) => c.id === expense.concept_id)?.name ?? '—'}</td>
              <td className="px-4 py-2 text-text-muted">{expense.notes ?? '—'}</td>
              <td className="px-4 py-2 text-text-muted">${expense.amount}</td>
              {canAdd && (
                <td className="px-4 py-2 text-right">
                  <button onClick={() => onDelete(expense)} className="text-text-muted hover:text-danger">
                    Eliminar
                  </button>
                </td>
              )}
            </tr>
          ))}
          {expenses.length === 0 && (
            <tr>
              <td colSpan={canAdd ? 4 : 3} className="px-4 py-6 text-center text-text-muted">
                Sin gastos registrados.
              </td>
            </tr>
          )}
        </tbody>
        {expenses.length > 0 && (
          <tfoot>
            <tr className="border-t border-border font-medium">
              <td className="px-4 py-2" colSpan={2}>
                Total
              </td>
              <td className="px-4 py-2">${total.toFixed(2)}</td>
              {canAdd && <td />}
            </tr>
          </tfoot>
        )}
      </table>

      {canAdd && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 border-t border-border p-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="concept">
              Concepto
            </label>
            <select
              id="concept"
              value={conceptId}
              onChange={(e) => setConceptId(e.target.value)}
              required
              className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              <option value="">Selecciona…</option>
              {concepts.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <Input
            id="amount"
            label="Monto"
            type="number"
            min={0}
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <Input id="notes" label="Notas" value={notes} onChange={(e) => setNotes(e.target.value)} />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Agregando…' : 'Agregar gasto'}
          </Button>
        </form>
      )}
    </div>
  )
}
