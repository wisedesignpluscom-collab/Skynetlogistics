import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useDriverDocumentTypes } from '../../features/driverDocuments/hooks'
import { createDriverDocumentType } from '../../features/driverDocuments/api'
import type { DriverDocumentPayload } from '../../features/driverDocuments/api'

interface DriverDocumentFormModalProps {
  onClose: () => void
  onSubmit: (values: DriverDocumentPayload) => Promise<void>
}

export function DriverDocumentFormModal({ onClose, onSubmit }: DriverDocumentFormModalProps) {
  const { types, isLoading, reload } = useDriverDocumentTypes()
  const [documentTypeId, setDocumentTypeId] = useState('')
  const [number, setNumber] = useState('')
  const [expiryDate, setExpiryDate] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [showNewType, setShowNewType] = useState(false)
  const [newTypeName, setNewTypeName] = useState('')
  const [newTypeAlertDays, setNewTypeAlertDays] = useState('60')

  async function handleCreateType() {
    const created = await createDriverDocumentType({
      name: newTypeName,
      alert_days_before: Number(newTypeAlertDays),
    })
    await reload()
    setDocumentTypeId(created.id)
    setShowNewType(false)
    setNewTypeName('')
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        document_type_id: documentTypeId,
        number: number || null,
        expiry_date: expiryDate || null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo guardar el documento')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo documento" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="document_type">
            Tipo de documento
          </label>
          <select
            id="document_type"
            value={documentTypeId}
            onChange={(e) => setDocumentTypeId(e.target.value)}
            required
            disabled={isLoading}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="">Selecciona un tipo</option>
            {types.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} (aviso {t.alert_days_before} días antes)
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setShowNewType((v) => !v)}
            className="mt-1 self-start text-xs text-gold hover:underline"
          >
            + Nuevo tipo de documento
          </button>
        </div>

        {showNewType && (
          <div className="flex flex-col gap-3 rounded-lg border border-border p-3">
            <Input
              id="new_type_name"
              label="Nombre del tipo"
              value={newTypeName}
              onChange={(e) => setNewTypeName(e.target.value)}
            />
            <Input
              id="new_type_alert_days"
              label="Días de aviso antes del vencimiento"
              type="number"
              min={0}
              value={newTypeAlertDays}
              onChange={(e) => setNewTypeAlertDays(e.target.value)}
            />
            <Button type="button" variant="secondary" onClick={handleCreateType} disabled={!newTypeName}>
              Crear tipo
            </Button>
          </div>
        )}

        <Input id="number" label="Número" value={number} onChange={(e) => setNumber(e.target.value)} />
        <Input
          id="expiry_date"
          label="Fecha de vencimiento"
          type="date"
          value={expiryDate}
          onChange={(e) => setExpiryDate(e.target.value)}
        />
        <Input id="notes" label="Observaciones" value={notes} onChange={(e) => setNotes(e.target.value)} />

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting || !documentTypeId}>
            {isSubmitting ? 'Guardando…' : 'Guardar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
