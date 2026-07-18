import type { ReactNode } from 'react'

type Tone = 'gold' | 'muted' | 'danger'

interface BadgeProps {
  tone?: Tone
  children: ReactNode
}

const toneClasses: Record<Tone, string> = {
  gold: 'bg-gold/15 text-gold-soft border-gold/30',
  muted: 'bg-surface-hover text-text-muted border-border',
  danger: 'bg-danger/15 text-danger border-danger/30',
}

export function Badge({ tone = 'muted', children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${toneClasses[tone]}`}>
      {children}
    </span>
  )
}
