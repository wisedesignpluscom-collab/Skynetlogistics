import { NavLink } from 'react-router-dom'

const upcomingModules = [
  'Vehículos',
  'Mantenimiento',
  'Viajes',
  'Neumáticos',
  'Inventario',
  'GPS',
  'Reportes',
]

export function Sidebar() {
  return (
    <aside className="flex w-60 flex-col border-r border-border bg-surface">
      <div className="border-b border-border px-6 py-5">
        <p className="font-display text-lg text-gold">Skynet</p>
        <p className="text-xs text-text-muted">Logistics</p>
      </div>
      <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
        <NavLink
          to="/users"
          className={({ isActive }) =>
            `rounded-md px-3 py-2 text-sm transition-colors ${
              isActive ? 'bg-gold/10 text-gold' : 'text-text-muted hover:bg-surface-hover hover:text-text'
            }`
          }
        >
          Usuarios
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
