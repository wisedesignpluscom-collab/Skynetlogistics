import type { ReactNode } from 'react'

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="font-display text-3xl text-gold">Skynet Logistics</h1>
          <p className="mt-1 text-sm text-text-muted">Gestión de flota</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-8 shadow-xl">{children}</div>
      </div>
    </div>
  )
}
