import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { RateTableSection } from '../components/tripSettings/RateTableSection'
import { DriverPayRateSection } from '../components/tripSettings/DriverPayRateSection'
import { HolidaySection } from '../components/tripSettings/HolidaySection'
import { ExpenseConceptSection } from '../components/tripSettings/ExpenseConceptSection'
import { useAuth } from '../features/auth/AuthContext'

type Tab = 'rates' | 'pay' | 'holidays' | 'concepts'

const TABS: { id: Tab; label: string }[] = [
  { id: 'rates', label: 'Tabulado de flete' },
  { id: 'pay', label: 'Pago a conductores' },
  { id: 'holidays', label: 'Feriados' },
  { id: 'concepts', label: 'Conceptos de gasto' },
]

export function TripSettingsPage() {
  const { hasPermission } = useAuth()
  const [tab, setTab] = useState<Tab>('rates')
  const canWrite = hasPermission('trip_settings', 'write')

  return (
    <DashboardLayout>
      <Link to="/trips" className="text-sm text-text-muted hover:text-gold">
        ← Volver a viajes
      </Link>
      <h1 className="mt-4 mb-6 font-display text-2xl text-text">Tabulados de viajes</h1>

      <div className="mb-6 flex gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm transition-colors ${
              tab === t.id
                ? 'border-b-2 border-gold text-gold'
                : 'text-text-muted hover:text-text'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'rates' && <RateTableSection canWrite={canWrite} />}
      {tab === 'pay' && <DriverPayRateSection canWrite={canWrite} />}
      {tab === 'holidays' && <HolidaySection canWrite={canWrite} />}
      {tab === 'concepts' && <ExpenseConceptSection canWrite={canWrite} />}
    </DashboardLayout>
  )
}
