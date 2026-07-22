import type { ReactNode } from 'react'

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gold text-xl font-bold text-white">
            S
          </div>
          <h1 className="font-display text-2xl font-semibold text-text">Skynet Logistics</h1>
          <p className="mt-1 text-sm text-text-muted">Gestión de flota</p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-8 shadow-xl shadow-slate-900/5">{children}</div>
      </div>
    </div>
  )
}
