import { NavLink } from 'react-router-dom'
import { useUnreadAlertCount } from '../../features/alerts/hooks'

const upcomingModules = ['Neumáticos', 'Inventario', 'Reportes']

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center justify-between rounded-md px-3 py-2 text-sm transition-colors ${
    isActive ? 'bg-gold/10 text-gold' : 'text-text-muted hover:bg-surface-hover hover:text-text'
  }`

export function Sidebar() {
  const { count } = useUnreadAlertCount()

  return (
    <aside className="flex w-60 flex-col border-r border-border bg-surface">
      <div className="border-b border-border px-6 py-5">
        <p className="font-display text-lg text-gold">Skynet</p>
        <p className="text-xs text-text-muted">Logistics</p>
      </div>
      <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
        <NavLink to="/users" className={navLinkClass}>
          Usuarios
        </NavLink>
        <NavLink to="/vehicles" className={navLinkClass}>
          Vehículos
        </NavLink>
        <NavLink to="/drivers" className={navLinkClass}>
          Conductores
        </NavLink>
        <NavLink to="/trips" className={navLinkClass}>
          Viajes
        </NavLink>
        <NavLink to="/gps-map" className={navLinkClass}>
          Mapa GPS
        </NavLink>
        <NavLink to="/alerts" className={navLinkClass}>
          <span>Alertas</span>
          {count > 0 && (
            <span className="rounded-full bg-gold px-2 py-0.5 text-xs font-semibold text-background">
              {count}
            </span>
          )}
        </NavLink>

        <p className="mt-6 px-3 text-xs uppercase tracking-wide text-text-muted/60">Próximamente</p>
        {upcomingModules.map((module) => (
          <span key={module} className="cursor-not-allowed rounded-md px-3 py-2 text-sm text-text-muted/40">
            {module}
          </span>
        ))}
      </nav>
    </aside>
  )
}
