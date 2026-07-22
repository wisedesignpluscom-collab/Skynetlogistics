import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { Company } from '../../types/company'
import type { CompanyPayload } from '../../features/companies/api'

interface CompanyFormModalProps {
  mode: 'create' | 'edit'
  initialCompany?: Company
  onClose: () => void
  onSubmit: (values: CompanyPayload) => Promise<void>
}

export function CompanyFormModal({ mode, initialCompany, onClose, onSubmit }: CompanyFormModalProps) {
  const [name, setName] = useState(initialCompany?.name ?? '')
  const [taxId, setTaxId] = useState(initialCompany?.tax_id ?? '')
  const [plan, setPlan] = useState(initialCompany?.plan ?? 'trial')
  const [contactPerson, setContactPerson] = useState(initialCompany?.contact_person ?? '')
  const [phone, setPhone] = useState(initialCompany?.phone ?? '')
  const [mobilePhone, setMobilePhone] = useState(initialCompany?.mobile_phone ?? '')
  const [email, setEmail] = useState(initialCompany?.email ?? '')
  const [address, setAddress] = useState(initialCompany?.address ?? '')
  const [city, setCity] = useState(initialCompany?.city ?? '')
  const [state, setState] = useState(initialCompany?.state ?? '')
  const [country, setCountry] = useState(initialCompany?.country ?? '')
  const [logoUrl, setLogoUrl] = useState(initialCompany?.logo_url ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        name,
        tax_id: taxId,
        plan,
        contact_person: contactPerson || null,
        phone: phone || null,
        mobile_phone: mobilePhone || null,
        email: email || null,
        address: address || null,
        city: city || null,
        state: state || null,
        country: country || null,
        logo_url: logoUrl || null,
      })
      onClose()
    } catch {
      setError('No se pudo guardar la empresa')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nueva empresa' : 'Editar empresa'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
          <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input id="tax_id" label="RIF / Tax ID" value={taxId} onChange={(e) => setTaxId(e.target.value)} required />
        </div>

        <Input id="plan" label="Plan" value={plan} onChange={(e) => setPlan(e.target.value)} />

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
          <Input id="phone" label="Teléfono principal" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <Input id="mobile_phone" label="Teléfono móvil" value={mobilePhone} onChange={(e) => setMobilePhone(e.target.value)} />
        </div>

        <Input id="address" label="Dirección" value={address} onChange={(e) => setAddress(e.target.value)} />

        <div className="grid grid-cols-3 gap-4">
          <Input id="city" label="Ciudad" value={city} onChange={(e) => setCity(e.target.value)} />
          <Input id="state" label="Estado" value={state} onChange={(e) => setState(e.target.value)} />
          <Input id="country" label="País" value={country} onChange={(e) => setCountry(e.target.value)} />
        </div>

        <Input
          id="logo_url"
          label="URL del logo"
          value={logoUrl}
          onChange={(e) => setLogoUrl(e.target.value)}
          placeholder="https://…"
        />

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
