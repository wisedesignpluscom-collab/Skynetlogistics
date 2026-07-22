import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { DriverDocumentsTable } from '../components/drivers/DriverDocumentsTable'
import { DriverDocumentFormModal } from '../components/drivers/DriverDocumentFormModal'
import { getDriver } from '../features/drivers/api'
import { useDriverFatigueHistory } from '../features/fatigue/hooks'
import { useDriverDocuments } from '../features/driverDocuments/hooks'
import { createDriverDocument, deleteDriverDocument } from '../features/driverDocuments/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Driver } from '../types/driver'
import type { DriverDocument } from '../types/driver_document'
import type { DriverFatigueLog, FatigueRiskLevel } from '../types/fatigue'

const statusTone = {
  activo: 'gold',
  suspendido: 'muted',
  inactivo: 'danger',
} as const

const riskTone: Record<FatigueRiskLevel, 'gold' | 'muted' | 'danger'> = {
  bajo: 'muted',
  medio: 'gold',
  alto: 'danger',
  critico: 'danger',
}

const riskBarColor: Record<FatigueRiskLevel, string> = {
  bajo: '#6b7280',
  medio: '#c9a227',
  alto: '#e0623a',
  critico: '#dc2626',
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

function daysAgoIso(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 10)
}

function RiskHistoryChart({ history }: { history: DriverFatigueLog[] }) {
  if (history.length === 0) {
    return <p className="text-text-muted">Sin datos de fatiga en el rango seleccionado.</p>
  }

  const maxScore = Math.max(150, ...history.map((h) => h.risk_score))

  return (
    <div className="flex items-end gap-2 overflow-x-auto rounded-lg border border-border p-4" style={{ height: 180 }}>
      {history.map((log) => {
        const heightPct = (log.risk_score / maxScore) * 100
        return (
          <div key={log.id} className="flex min-w-[36px] flex-col items-center justify-end gap-1" style={{ height: '100%' }}>
            <span className="text-xs text-text-muted">{log.risk_score}</span>
            <div
              className="w-4 rounded-t"
              style={{ height: `${heightPct}%`, backgroundColor: riskBarColor[log.risk_level] }}
              title={`${log.date}: ${log.risk_level} (${log.risk_score})`}
            />
            <span className="whitespace-nowrap text-[10px] text-text-muted">{log.date.slice(5)}</span>
          </div>
        )
      })}
    </div>
  )
}

export function DriverDetailPage() {
  const { driverId } = useParams<{ driverId: string }>()
  const { hasPermission } = useAuth()
  const [driver, setDriver] = useState<Driver | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const dateFrom = daysAgoIso(14)
  const dateTo = todayIso()
  const { history, isLoading: isHistoryLoading } = useDriverFatigueHistory(driverId, dateFrom, dateTo)
  const { documents, reload: reloadDocuments } = useDriverDocuments(driverId)
  const [showDocumentModal, setShowDocumentModal] = useState(false)
  const canWrite = hasPermission('drivers', 'write')

  const reload = useCallback(async () => {
    if (!driverId) return
    setIsLoading(true)
    setDriver(await getDriver(driverId))
    setIsLoading(false)
  }, [driverId])

  useEffect(() => {
    void reload()
  }, [reload])

  const latest = history.length > 0 ? history[history.length - 1] : null

  async function handleDeleteDocument(document: DriverDocument) {
    if (!window.confirm('¿Eliminar este documento?')) return
    await deleteDriverDocument(document.id)
    await reloadDocuments()
  }

  if (isLoading || !driver) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <Link to="/drivers" className="text-sm text-text-muted hover:text-gold">
        ← Volver a conductores
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">{driver.name}</h1>
          <p className="text-text-muted">
            Licencia {driver.license_number} · Vence {driver.license_expiry}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {latest && <Badge tone={riskTone[latest.risk_level]}>Riesgo {latest.risk_level}</Badge>}
          <Badge tone={statusTone[driver.status]}>{driver.status}</Badge>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-x-8 gap-y-2 rounded-lg border border-border p-4 text-sm md:grid-cols-4">
        <div>
          <p className="text-text-muted">Correo</p>
          <p className="text-text">{driver.email || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Teléfono secundario</p>
          <p className="text-text">{driver.secondary_phone || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Dirección</p>
          <p className="text-text">
            {[driver.address, driver.city, driver.state, driver.country].filter(Boolean).join(', ') || '—'}
          </p>
        </div>
        <div>
          <p className="text-text-muted">Fecha de nacimiento</p>
          <p className="text-text">{driver.birth_date || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Sueldo base</p>
          <p className="text-text">{driver.base_salary != null ? `$${driver.base_salary}` : '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Período de pago</p>
          <p className="text-text">{driver.pay_period || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Fecha de ingreso</p>
          <p className="text-text">{driver.hire_date || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Fecha de egreso</p>
          <p className="text-text">{driver.termination_date || '—'}</p>
        </div>
        {driver.notes && (
          <div className="col-span-full">
            <p className="text-text-muted">Observaciones</p>
            <p className="text-text">{driver.notes}</p>
          </div>
        )}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg text-text">Documentos</h2>
        {canWrite && <Button onClick={() => setShowDocumentModal(true)}>Agregar documento</Button>}
      </div>
      <div className="mb-8">
        <DriverDocumentsTable documents={documents} canWrite={canWrite} onDelete={handleDeleteDocument} />
      </div>

      {showDocumentModal && driverId && (
        <DriverDocumentFormModal
          onClose={() => setShowDocumentModal(false)}
          onSubmit={async (values) => {
            await createDriverDocument(driverId, values)
            await reloadDocuments()
          }}
        />
      )}

      <h2 className="mb-4 font-display text-lg text-text">Historial de riesgo de fatiga (últimos 14 días)</h2>

      {isHistoryLoading && <p className="text-text-muted">Cargando historial…</p>}
      {!isHistoryLoading && <RiskHistoryChart history={history} />}

      {history.length > 0 && (
        <div className="mt-4 overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Fecha</th>
                <th className="px-4 py-2 font-medium">Manejo continuo (min)</th>
                <th className="px-4 py-2 font-medium">Total 24h (min)</th>
                <th className="px-4 py-2 font-medium">Total 7 días (min)</th>
                <th className="px-4 py-2 font-medium">Manejo nocturno (min)</th>
                <th className="px-4 py-2 font-medium">Score</th>
                <th className="px-4 py-2 font-medium">Nivel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {[...history].reverse().map((log) => (
                <tr key={log.id}>
                  <td className="px-4 py-2 text-text-muted">{log.date}</td>
                  <td className="px-4 py-2 text-text-muted">{log.continuous_driving_min}</td>
                  <td className="px-4 py-2 text-text-muted">{log.total_24h_min}</td>
                  <td className="px-4 py-2 text-text-muted">{log.total_7day_min}</td>
                  <td className="px-4 py-2 text-text-muted">{log.night_driving_min}</td>
                  <td className="px-4 py-2 text-text-muted">{log.risk_score}</td>
                  <td className="px-4 py-2">
                    <Badge tone={riskTone[log.risk_level]}>{log.risk_level}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardLayout>
  )
}
