import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import type { Client } from '../../types/client'
import type { ClientPayload } from '../../features/clients/api'
import type { CustomData } from '../../types/customField'

interface ClientFormModalProps {
  mode: 'create' | 'edit'
  initialClient?: Client
  onClose: () => void
  onSubmit: (values: ClientPayload) => Promise<void>
}

export function ClientFormModal({ mode, initialClient, onClose, onSubmit }: ClientFormModalProps) {
  const [name, setName] = useState(initialClient?.name ?? '')
  const [taxId, setTaxId] = useState(initialClient?.tax_id ?? '')
  const [contactPerson, setContactPerson] = useState(initialClient?.contact_person ?? '')
  const [address, setAddress] = useState(initialClient?.address ?? '')
  const [phone, setPhone] = useState(initialClient?.phone ?? '')
  const [email, setEmail] = useState(initialClient?.email ?? '')
  const [defaultCargoType, setDefaultCargoType] = useState(initialClient?.default_cargo_type ?? '')
  const [customData, setCustomData] = useState<CustomData>(initialClient?.custom_data ?? {})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules('client', { default_cargo_type: defaultCargoType }, customData)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        name,
        tax_id: taxId || null,
        contact_person: contactPerson || null,
        address: address || null,
        phone: phone || null,
        email: email || null,
        default_cargo_type: defaultCargoType || null,
        custom_data: customData,
      })
      onClose()
    } catch {
      setError('No se pudo guardar el cliente')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo cliente' : 'Editar cliente'} onClose={onClose}>
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
          <Input id="email" label="Correo electrónico" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input id="phone" label="Teléfono" value={phone} onChange={(e) => setPhone(e.target.value)} />
          {!rules.isHidden('default_cargo_type') && (
            <Input
              id="default_cargo_type"
              label={rules.isRequired('default_cargo_type') ? 'Tipo de carga predeterminado *' : 'Tipo de carga predeterminado'}
              value={defaultCargoType}
              onChange={(e) => setDefaultCargoType(e.target.value)}
              required={rules.isRequired('default_cargo_type')}
            />
          )}
        </div>

        <Input id="address" label="Dirección" value={address} onChange={(e) => setAddress(e.target.value)} />

        <CustomFieldsSection entityType="client" value={customData} onChange={setCustomData} rules={rules} />

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
