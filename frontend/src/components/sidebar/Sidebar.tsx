import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useUnreadAlertCount } from '../../features/alerts/hooks'
import { useAuth } from '../../features/auth/AuthContext'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? 'bg-white/15 text-white'
      : 'text-[color:var(--color-sidebar-muted)] hover:bg-[color:var(--color-sidebar-hover)] hover:text-white'
  }`

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      className="h-[18px] w-[18px] shrink-0"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {children}
    </svg>
  )
}

const icons = {
  companies: <><path d="M3 21h18" /><path d="M5 21V7l7-4 7 4v14" /><path d="M9 21v-6h6v6" /></>,
  users: <><circle cx="9" cy="7" r="3" /><path d="M2 21v-1a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v1" /><path d="M17 11l2 2 4-4" /></>,
  vehicles: <><path d="M3 13l1.5-4.5A2 2 0 0 1 6.4 7h7.2a2 2 0 0 1 1.9 1.5L17 13" /><path d="M3 13h14v4H3z" /><circle cx="6.5" cy="17.5" r="1.5" /><circle cx="13.5" cy="17.5" r="1.5" /><path d="M17 10h2.5a2 2 0 0 1 1.8 1.1L22 13v4h-2" /></>,
  drivers: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  trips: <><path d="M3 7h13l3 4v6h-3" /><path d="M3 7v10h3" /><circle cx="8" cy="17" r="1.6" /><circle cx="17" cy="17" r="1.6" /></>,
  map: <><path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z" /><path d="M9 4v14M15 6v14" /></>,
  tires: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3.5" /><path d="M12 3v5M12 16v5M3 12h5M16 12h5" /></>,
  inventory: <><path d="M3 7l9-4 9 4-9 4-9-4z" /><path d="M3 7v10l9 4 9-4V7" /><path d="M12 11v10" /></>,
  delivery: <><rect x="2" y="6" width="13" height="10" rx="1.5" /><path d="M15 9h4l2 3v4h-6" /><circle cx="7" cy="18" r="1.6" /><circle cx="17" cy="18" r="1.6" /></>,
  reports: <><path d="M8 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-2" /><rect x="8" y="2" width="8" height="4" rx="1" /><path d="M9 13l2 2 4-4" /></>,
  alerts: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 0 1-3.4 0" /></>,
  config: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></>,
}

export function Sidebar() {
  const { count } = useUnreadAlertCount()
  const { user, hasPermission } = useAuth()

  return (
    <aside className="flex w-60 flex-col bg-[color:var(--color-sidebar)]">
      <div className="flex items-center gap-2 px-6 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 text-lg font-bold text-white">
          S
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight text-white">Skynet</p>
          <p className="text-xs leading-tight text-[color:var(--color-sidebar-muted)]">Logistics</p>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
        {user?.is_superadmin && (
          <NavLink to="/companies" className={navLinkClass}>
            <span className="flex items-center gap-3"><Icon>{icons.companies}</Icon>Empresas</span>
          </NavLink>
        )}
        <NavLink to="/users" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.users}</Icon>Usuarios</span>
        </NavLink>
        <NavLink to="/vehicles" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.vehicles}</Icon>Vehículos</span>
        </NavLink>
        <NavLink to="/drivers" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.drivers}</Icon>Conductores</span>
        </NavLink>
        <NavLink to="/trips" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.trips}</Icon>Viajes</span>
        </NavLink>
        <NavLink to="/gps-map" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.map}</Icon>Mapa GPS</span>
        </NavLink>
        <NavLink to="/tires" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.tires}</Icon>Neumáticos</span>
        </NavLink>
        <NavLink to="/inventory" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.inventory}</Icon>Inventario</span>
        </NavLink>
        {hasPermission('delivery', 'read') && (
          <NavLink to="/delivery-orders" className={navLinkClass}>
            <span className="flex items-center gap-3"><Icon>{icons.delivery}</Icon>Reparto</span>
          </NavLink>
        )}
        {hasPermission('incidents', 'read') && (
          <NavLink to="/incidents" className={navLinkClass}>
            <span className="flex items-center gap-3"><Icon>{icons.reports}</Icon>Reportes</span>
          </NavLink>
        )}
        {hasPermission('config', 'read') && (
          <NavLink to="/config" className={navLinkClass}>
            <span className="flex items-center gap-3"><Icon>{icons.config}</Icon>Configuración</span>
          </NavLink>
        )}
        <NavLink to="/alerts" className={navLinkClass}>
          <span className="flex items-center gap-3"><Icon>{icons.alerts}</Icon>Alertas</span>
          {count > 0 && (
            <span className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold text-[color:var(--color-sidebar)]">
              {count}
            </span>
          )}
        </NavLink>
      </nav>
    </aside>
  )
}
