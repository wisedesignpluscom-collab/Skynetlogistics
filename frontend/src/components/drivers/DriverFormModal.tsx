import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { Driver, DriverStatus } from '../../types/driver'
import type { DriverPayload, DriverUpdatePayload } from '../../features/drivers/api'

const DRIVER_STATUSES: DriverStatus[] = ['activo', 'suspendido', 'inactivo']

interface DriverFormModalProps {
  mode: 'create' | 'edit'
  initialDriver?: Driver
  onClose: () => void
  onSubmit: (values: DriverPayload | DriverUpdatePayload) => Promise<void>
}

export function DriverFormModal({ mode, initialDriver, onClose, onSubmit }: DriverFormModalProps) {
  const [name, setName] = useState(initialDriver?.name ?? '')
  const [licenseNumber, setLicenseNumber] = useState(initialDriver?.license_number ?? '')
  const [licenseExpiry, setLicenseExpiry] = useState(initialDriver?.license_expiry ?? '')
  const [phone, setPhone] = useState(initialDriver?.phone ?? '')
  const [status, setStatus] = useState<DriverStatus>(initialDriver?.status ?? 'activo')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      if (mode === 'create') {
        await onSubmit({
          name,
          license_number: licenseNumber,
          license_expiry: licenseExpiry,
          phone: phone || null,
        })
      } else {
        await onSubmit({
          name,
          license_number: licenseNumber,
          license_expiry: licenseExpiry,
          phone: phone || null,
          status,
        })
      }
      onClose()
    } catch {
      setError('No se pudo guardar el conductor')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo conductor' : 'Editar conductor'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
        <Input
          id="license_number"
          label="Número de licencia"
          value={licenseNumber}
          onChange={(e) => setLicenseNumber(e.target.value)}
          required
        />
        <Input
          id="license_expiry"
          label="Vencimiento de licencia"
          type="date"
          value={licenseExpiry}
          onChange={(e) => setLicenseExpiry(e.target.value)}
          required
        />
        <Input id="phone" label="Teléfono" value={phone} onChange={(e) => setPhone(e.target.value)} />
        {mode === 'edit' && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="status">
              Estado
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value as DriverStatus)}
              className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
            >
              {DRIVER_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        )}
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
