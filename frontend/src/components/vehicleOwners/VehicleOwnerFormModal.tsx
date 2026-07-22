import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { VehicleOwner } from '../../types/vehicle_owner'
import type { VehicleOwnerPayload } from '../../features/vehicleOwners/api'

interface VehicleOwnerFormModalProps {
  mode: 'create' | 'edit'
  initialOwner?: VehicleOwner
  onClose: () => void
  onSubmit: (values: VehicleOwnerPayload) => Promise<void>
}

export function VehicleOwnerFormModal({ mode, initialOwner, onClose, onSubmit }: VehicleOwnerFormModalProps) {
  const [name, setName] = useState(initialOwner?.name ?? '')
  const [taxId, setTaxId] = useState(initialOwner?.tax_id ?? '')
  const [contactPerson, setContactPerson] = useState(initialOwner?.contact_person ?? '')
  const [phone, setPhone] = useState(initialOwner?.phone ?? '')
  const [email, setEmail] = useState(initialOwner?.email ?? '')
  const [notes, setNotes] = useState(initialOwner?.notes ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        name,
        tax_id: taxId || null,
        contact_person: contactPerson || null,
        phone: phone || null,
        email: email || null,
        notes: notes || null,
      })
      onClose()
    } catch {
      setError('No se pudo guardar el propietario')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo propietario' : 'Editar propietario'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
          <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input id="tax_id" label="RIF / Tax ID" value={taxId} onChange={(e) => setTaxId(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input
            id="contact_person"
            label="Persona de contacto"
            value={contactPerson}
            onChange={(e) => setContactPerson(e.target.value)}
          />
          <Input id="phone" label="Teléfono" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <Input id="email" label="Correo electrónico" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input id="notes" label="Observaciones" value={notes} onChange={(e) => setNotes(e.target.value)} />

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
