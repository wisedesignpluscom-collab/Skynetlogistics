import { useEffect, useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import { useSystemFieldRules } from '../../features/config/useSystemFieldRules'
import type { Driver, DriverStatus, PayPeriod } from '../../types/driver'
import type { DriverPayload, DriverUpdatePayload } from '../../features/drivers/api'
import type { CustomData } from '../../types/customField'

const DRIVER_STATUSES: DriverStatus[] = ['activo', 'suspendido', 'inactivo']
const PAY_PERIODS: PayPeriod[] = ['semanal', 'quincenal', 'mensual']

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

  const [birthDate, setBirthDate] = useState(initialDriver?.birth_date ?? '')
  const [address, setAddress] = useState(initialDriver?.address ?? '')
  const [city, setCity] = useState(initialDriver?.city ?? '')
  const [state, setState] = useState(initialDriver?.state ?? '')
  const [country, setCountry] = useState(initialDriver?.country ?? '')
  const [email, setEmail] = useState(initialDriver?.email ?? '')
  const [secondaryPhone, setSecondaryPhone] = useState(initialDriver?.secondary_phone ?? '')
  const [notes, setNotes] = useState(initialDriver?.notes ?? '')

  const [baseSalary, setBaseSalary] = useState(initialDriver?.base_salary?.toString() ?? '')
  const [payPeriod, setPayPeriod] = useState<PayPeriod | ''>(initialDriver?.pay_period ?? '')
  const [hireDate, setHireDate] = useState(initialDriver?.hire_date ?? '')
  const [terminationDate, setTerminationDate] = useState(initialDriver?.termination_date ?? '')
  const [customData, setCustomData] = useState<CustomData>(initialDriver?.custom_data ?? {})

  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const rules = useSystemFieldRules(
    'driver',
    { status, license_expiry: licenseExpiry, base_salary: baseSalary, pay_period: payPeriod },
    customData
  )

  useEffect(() => {
    const setters: Record<string, (v: string) => void> = {
      license_expiry: setLicenseExpiry,
      base_salary: setBaseSalary,
    }
    for (const [key, computedVal] of Object.entries(rules.computed)) {
      setters[key]?.(String(computedVal))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(rules.computed)])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const base: DriverPayload = {
        name,
        license_number: licenseNumber,
        license_expiry: licenseExpiry,
        phone: phone || null,
        birth_date: birthDate || null,
        address: address || null,
        city: city || null,
        state: state || null,
        country: country || null,
        email: email || null,
        secondary_phone: secondaryPhone || null,
        notes: notes || null,
        base_salary: baseSalary ? Number(baseSalary) : null,
        pay_period: payPeriod || null,
        hire_date: hireDate || null,
        termination_date: terminationDate || null,
        custom_data: customData,
      }
      await onSubmit(mode === 'create' ? base : { ...base, status })
      onClose()
    } catch {
      setError('No se pudo guardar el conductor')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={mode === 'create' ? 'Nuevo conductor' : 'Editar conductor'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <Input id="name" label="Nombre" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input
            id="birth_date"
            label="Fecha de nacimiento"
            type="date"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            id="license_number"
            label="Número de licencia"
            value={licenseNumber}
            onChange={(e) => setLicenseNumber(e.target.value)}
            required
          />
          {!rules.isHidden('license_expiry') && (
            <Input
              id="license_expiry"
              label={rules.isRequired('license_expiry') ? 'Vencimiento de licencia *' : 'Vencimiento de licencia'}
              type="date"
              value={licenseExpiry}
              onChange={(e) => setLicenseExpiry(e.target.value)}
              required
            />
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input id="phone" label="Teléfono" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <Input
            id="secondary_phone"
            label="Teléfono secundario"
            value={secondaryPhone}
            onChange={(e) => setSecondaryPhone(e.target.value)}
          />
        </div>

        <Input id="email" label="Correo electrónico" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input id="address" label="Dirección" value={address} onChange={(e) => setAddress(e.target.value)} />

        <div className="grid grid-cols-3 gap-4">
          <Input id="city" label="Ciudad" value={city} onChange={(e) => setCity(e.target.value)} />
          <Input id="state" label="Estado" value={state} onChange={(e) => setState(e.target.value)} />
          <Input id="country" label="País" value={country} onChange={(e) => setCountry(e.target.value)} />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="notes">
            Observaciones
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {!rules.isHidden('base_salary') && (
            <Input
              id="base_salary"
              label={rules.isRequired('base_salary') ? 'Sueldo base *' : 'Sueldo base'}
              type="number"
              step="any"
              min={0}
              value={baseSalary}
              onChange={(e) => setBaseSalary(e.target.value)}
              required={rules.isRequired('base_salary')}
            />
          )}
          {!rules.isHidden('pay_period') && (
            <div className="flex flex-col gap-1">
              <label className="text-sm text-text-muted" htmlFor="pay_period">
                {rules.isRequired('pay_period') ? 'Período de pago *' : 'Período de pago'}
              </label>
              <select
                id="pay_period"
                value={payPeriod}
                onChange={(e) => setPayPeriod(e.target.value as PayPeriod | '')}
                className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              >
                <option value="">Sin especificar</option>
                {PAY_PERIODS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            id="hire_date"
            label="Fecha de ingreso"
            type="date"
            value={hireDate}
            onChange={(e) => setHireDate(e.target.value)}
          />
          <Input
            id="termination_date"
            label="Fecha de egreso"
            type="date"
            value={terminationDate}
            onChange={(e) => setTerminationDate(e.target.value)}
          />
        </div>

        {mode === 'edit' && !rules.isHidden('status') && (
          <div className="flex flex-col gap-1">
            <label className="text-sm text-text-muted" htmlFor="status">
              {rules.isRequired('status') ? 'Estado *' : 'Estado'}
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
        <CustomFieldsSection
          entityType="driver"
          value={customData}
          onChange={setCustomData}
          systemValues={{ status, license_expiry: licenseExpiry, base_salary: baseSalary, pay_period: payPeriod }}
          rules={rules}
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
