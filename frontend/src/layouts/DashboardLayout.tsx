import type { ReactNode } from 'react'
import { Sidebar } from '../components/sidebar/Sidebar'
import { useAuth } from '../features/auth/AuthContext'

export function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-background text-text">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border px-6 py-4">
          <p className="text-sm text-text-muted">{user?.role.name}</p>
          <div className="flex items-center gap-4">
            <span className="text-sm">{user?.name}</span>
            <button onClick={() => void logout()} className="text-sm text-text-muted hover:text-gold">
              Cerrar sesión
            </button>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
