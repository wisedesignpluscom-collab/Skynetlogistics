import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { WarehousePayload } from '../../features/tires/api'
import type { Warehouse } from '../../types/tire'

interface WarehouseFormModalProps {
  initialWarehouse?: Warehouse
  onClose: () => void
  onSubmit: (values: WarehousePayload) => Promise<void>
}

export function WarehouseFormModal({ initialWarehouse, onClose, onSubmit }: WarehouseFormModalProps) {
  const [name, setName] = useState(initialWarehouse?.name ?? '')
  const [location, setLocation] = useState(initialWarehouse?.location ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({ name, location: location || null })
      onClose()
    } catch {
      setError('No se pudo guardar el almacén')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={initialWarehouse ? 'Editar almacén' : 'Nuevo almacén'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
        <Input id="location" label="Ubicación" value={location} onChange={(e) => setLocation(e.target.value)} />
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
    </Modal>
  )
}
