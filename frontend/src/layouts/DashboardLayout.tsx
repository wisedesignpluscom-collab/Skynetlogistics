import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Sidebar } from '../components/sidebar/Sidebar'
import { useAuth } from '../features/auth/AuthContext'

const SECTION_LABELS: Record<string, string> = {
  companies: 'Empresas',
  users: 'Usuarios',
  vehicles: 'Vehículos',
  drivers: 'Conductores',
  trips: 'Viajes',
  'gps-map': 'Mapa GPS',
  tires: 'Neumáticos',
  warehouses: 'Almacenes',
  inventory: 'Inventario',
  'delivery-orders': 'Reparto — Pedidos',
  'delivery-goods': 'Reparto — Mercancía',
  incidents: 'Reportes',
  alerts: 'Alertas',
}

function sectionLabel(pathname: string): string {
  const first = pathname.split('/').filter(Boolean)[0] ?? ''
  return SECTION_LABELS[first] ?? 'Panel'
}

function initials(name: string | undefined): string {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  return (parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')
}

export function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="flex min-h-screen bg-background text-text">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
          <p className="text-sm font-medium">
            <span className="text-gold">Principal</span>
            <span className="text-text-muted"> / {sectionLabel(location.pathname)}</span>
          </p>
          <div className="flex items-center gap-4">
            <button
              onClick={() => void logout()}
              className="text-sm text-text-muted transition-colors hover:text-gold"
            >
              Cerrar sesión
            </button>
            <div className="flex items-center gap-2">
              <span className="hidden text-sm text-text-muted sm:inline">{user?.name}</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gold text-xs font-semibold uppercase text-white">
                {initials(user?.name)}
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
