import { useState, type FormEvent } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useExpenseConcepts } from '../../features/tripSettings/hooks'
import { createExpenseConcept, deleteExpenseConcept } from '../../features/tripSettings/api'

export function ExpenseConceptSection({ canWrite }: { canWrite: boolean }) {
  const { concepts, isLoading, reload } = useExpenseConcepts()
  const [name, setName] = useState('')
  const [defaultLimit, setDefaultLimit] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await createExpenseConcept({ name, default_limit: defaultLimit ? Number(defaultLimit) : null })
      setName('')
      setDefaultLimit('')
      await reload()
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('¿Eliminar este concepto?')) return
    await deleteExpenseConcept(id)
    await reload()
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-text-muted">
            <tr>
              <th className="px-4 py-2 font-medium">Nombre</th>
              <th className="px-4 py-2 font-medium">Límite sugerido</th>
              {canWrite && <th className="px-4 py-2" />}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {concepts.map((c) => (
              <tr key={c.id}>
                <td className="px-4 py-2">{c.name}</td>
                <td className="px-4 py-2 text-text-muted">{c.default_limit !== null ? `$${c.default_limit}` : '—'}</td>
                {canWrite && (
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => handleDelete(c.id)} className="text-text-muted hover:text-danger">
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {!isLoading && concepts.length === 0 && (
              <tr>
                <td colSpan={canWrite ? 3 : 2} className="px-4 py-6 text-center text-text-muted">
                  No hay conceptos de gasto configurados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {canWrite && (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3 rounded-lg border border-border p-4">
          <Input id="concept_name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input
            id="concept_limit"
            label="Límite sugerido ($, opcional)"
            type="number"
            min={0}
            step="0.01"
            value={defaultLimit}
            onChange={(e) => setDefaultLimit(e.target.value)}
          />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Agregar'}
          </Button>
        </form>
      )}
    </div>
  )
}
