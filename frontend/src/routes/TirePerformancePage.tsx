import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { useTirePerformance } from '../features/tires/hooks'
import type { TireMovementType } from '../types/tire'

const END_REASON_LABELS: Record<TireMovementType, string> = {
  instalacion: 'Instalación',
  desinstalacion: 'Desinstalación',
  envio_reparacion: 'Reparación',
  envio_reencauche: 'Reencauche',
  retorno_taller: 'Retorno de taller',
}

export function TirePerformancePage() {
  const { rows, isLoading } = useTirePerformance()

  return (
    <DashboardLayout>
      <Link to="/tires" className="text-sm text-text-muted hover:text-gold">
        ← Volver a neumáticos
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="font-display text-2xl text-text">Rendimiento por marca / modelo</h1>
        <p className="text-sm text-text-muted">
          Kilómetros promedio recorridos hasta el envío a reparación o a reencauche, agrupados
          por marca y modelo.
        </p>
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      {!isLoading && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Marca</th>
                <th className="px-4 py-3 font-medium">Modelo</th>
                <th className="px-4 py-3 font-medium">Motivo de cierre</th>
                <th className="px-4 py-3 font-medium">Muestras</th>
                <th className="px-4 py-3 font-medium">Km promedio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows.map((row) => (
                <tr key={`${row.brand}-${row.model}-${row.end_reason}`} className="bg-background/40">
                  <td className="px-4 py-3 text-text">{row.brand}</td>
                  <td className="px-4 py-3 text-text-muted">{row.model}</td>
                  <td className="px-4 py-3 text-text-muted">{END_REASON_LABELS[row.end_reason]}</td>
                  <td className="px-4 py-3 text-text-muted">{row.sample_count}</td>
                  <td className="px-4 py-3 text-text-muted">{Math.round(row.avg_km).toLocaleString()} km</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                    Todavía no hay suficientes movimientos de reparación/reencauche para calcular rendimiento.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </DashboardLayout>
  )
}
