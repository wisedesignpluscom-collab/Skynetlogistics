import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'secondary' | 'danger'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
}

const variantClasses: Record<Variant, string> = {
  primary: 'bg-gold text-white shadow-sm shadow-gold/25 hover:bg-gold-soft disabled:bg-gold/40',
  secondary: 'border border-border bg-surface text-text hover:bg-surface-hover disabled:opacity-40',
  danger: 'bg-danger text-white hover:bg-danger/85 disabled:opacity-40',
}

export function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`}
      {...props}
    />
  )
}
