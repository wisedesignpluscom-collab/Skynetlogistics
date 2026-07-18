import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { MaintenanceHistoryTable } from '../components/maintenance/MaintenanceHistoryTable'
import { MaintenanceTaskFormModal } from '../components/maintenance/MaintenanceTaskFormModal'
import { CompleteTaskModal } from '../components/maintenance/CompleteTaskModal'
import { getVehicle } from '../features/vehicles/api'
import {
  completeMaintenanceTask,
  createMaintenanceTask,
  getVehicleMaintenanceHistory,
} from '../features/maintenance/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Vehicle } from '../types/vehicle'
import type { MaintenanceTaskWithRecords } from '../types/maintenance'

export function VehicleDetailPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>()
  const { hasPermission } = useAuth()
  const [vehicle, setVehicle] = useState<Vehicle | null>(null)
  const [tasks, setTasks] = useState<MaintenanceTaskWithRecords[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [completingTask, setCompletingTask] = useState<MaintenanceTaskWithRecords | null>(null)

  const canWrite = hasPermission('maintenance', 'write')

  const reload = useCallback(async () => {
    if (!vehicleId) return
    setIsLoading(true)
    const [v, history] = await Promise.all([
      getVehicle(vehicleId),
      getVehicleMaintenanceHistory(vehicleId),
    ])
    setVehicle(v)
    setTasks(history)
    setIsLoading(false)
  }, [vehicleId])

  useEffect(() => {
    void reload()
  }, [reload])

  if (isLoading || !vehicle) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">Cargando…</p>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <Link to="/vehicles" className="text-sm text-text-muted hover:text-gold">
        ← Volver a vehículos
      </Link>

      <div className="mt-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-text">{vehicle.plate}</h1>
          <p className="text-text-muted">
            {vehicle.brand} {vehicle.model} ({vehicle.year}) · {vehicle.current_odometer_km.toLocaleString()} km
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to={`/vehicles/${vehicle.id}/route`} className="text-sm text-text-muted hover:text-gold">
            Ver ruta GPS
          </Link>
          <Link to={`/vehicles/${vehicle.id}/tires`} className="text-sm text-text-muted hover:text-gold">
            Neumáticos
          </Link>
          <Badge tone={vehicle.status === 'activo' ? 'gold' : 'muted'}>{vehicle.status}</Badge>
        </div>
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg text-text">Historial de mantenimiento</h2>
        {canWrite && <Button onClick={() => setShowTaskModal(true)}>Programar mantenimiento</Button>}
      </div>

      <MaintenanceHistoryTable tasks={tasks} canComplete={canWrite} onComplete={setCompletingTask} />

      {showTaskModal && (
        <MaintenanceTaskFormModal
          vehicleId={vehicle.id}
          onClose={() => setShowTaskModal(false)}
          onSubmit={async (values) => {
            await createMaintenanceTask(values)
            await reload()
          }}
        />
      )}

      {completingTask && (
        <CompleteTaskModal
          onClose={() => setCompletingTask(null)}
          onSubmit={async (values) => {
            await completeMaintenanceTask(completingTask.id, values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
