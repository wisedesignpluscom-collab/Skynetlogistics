export type DriverStatus = 'activo' | 'suspendido' | 'inactivo'

export interface Driver {
  id: string
  company_id: string
  name: string
  license_number: string
  license_expiry: string
  phone: string | null
  status: DriverStatus
  created_at: string
  updated_at: string
}
