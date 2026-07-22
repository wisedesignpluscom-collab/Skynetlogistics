import type { ReactNode } from 'react'

type Tone = 'gold' | 'muted' | 'danger' | 'success' | 'warning'

interface BadgeProps {
  tone?: Tone
  children: ReactNode
}

const toneClasses: Record<Tone, string> = {
  gold: 'bg-gold/10 text-gold border-gold/20',
  muted: 'bg-surface-hover text-text-muted border-border',
  danger: 'bg-danger/10 text-danger border-danger/20',
  success: 'bg-emerald-50 text-emerald-600 border-emerald-200',
  warning: 'bg-amber-50 text-amber-600 border-amber-200',
}

export function Badge({ tone = 'muted', children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${toneClasses[tone]}`}>
      {children}
    </span>
  )
}
