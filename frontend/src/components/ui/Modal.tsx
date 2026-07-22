import type { ReactNode } from 'react'

interface ModalProps {
  title: string
  onClose: () => void
  children: ReactNode
}

export function Modal({ title, onClose, children }: ModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-xl border border-border bg-surface p-6 shadow-2xl shadow-slate-900/10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-lg font-semibold text-text">{title}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text" aria-label="Cerrar">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
