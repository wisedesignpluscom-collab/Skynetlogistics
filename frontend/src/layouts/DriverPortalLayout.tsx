import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'

export function DriverPortalLayout({ title, children }: { title: string; children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen flex-col bg-background text-text">
      <header className="flex items-center justify-between border-b border-border bg-surface px-4 py-4">
        <div>
          <Link to="/driver" className="font-display text-lg font-semibold text-gold">
            {title}
          </Link>
          <p className="text-xs text-text-muted">{user?.name}</p>
        </div>
        <button onClick={() => void logout()} className="text-sm text-text-muted hover:text-gold">
          Salir
        </button>
      </header>
      <main className="flex-1 px-4 py-4">{children}</main>
    </div>
  )
}
