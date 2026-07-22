import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { MaintenanceHistoryTable } from '../components/maintenance/MaintenanceHistoryTable'
import { MaintenanceTaskFormModal } from '../components/maintenance/MaintenanceTaskFormModal'
import { CompleteTaskModal } from '../components/maintenance/CompleteTaskModal'
import { MaintenanceSettingsModal } from '../components/maintenance/MaintenanceSettingsModal'
import { VehicleDocumentsTable } from '../components/vehicles/VehicleDocumentsTable'
import { VehicleDocumentFormModal } from '../components/vehicles/VehicleDocumentFormModal'
import { getVehicle } from '../features/vehicles/api'
import {
  completeMaintenanceTask,
  createMaintenanceTask,
  getVehicleMaintenanceHistory,
  updateMaintenanceSettings,
} from '../features/maintenance/api'
import { useVehicleDocuments } from '../features/vehicleDocuments/hooks'
import { createVehicleDocument, deleteVehicleDocument } from '../features/vehicleDocuments/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Vehicle } from '../types/vehicle'
import type { VehicleDocument } from '../types/vehicle_document'
import type { MaintenanceTaskWithRecords } from '../types/maintenance'

export function VehicleDetailPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>()
  const { hasPermission } = useAuth()
  const [vehicle, setVehicle] = useState<Vehicle | null>(null)
  const [tasks, setTasks] = useState<MaintenanceTaskWithRecords[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [completingTask, setCompletingTask] = useState<MaintenanceTaskWithRecords | null>(null)
  const { documents, reload: reloadDocuments } = useVehicleDocuments(vehicleId)
  const [showDocumentModal, setShowDocumentModal] = useState(false)

  const canWrite = hasPermission('maintenance', 'write')
  const canWriteVehicle = hasPermission('vehicles', 'write')

  async function handleDeleteDocument(document: VehicleDocument) {
    if (!window.confirm('¿Eliminar este documento?')) return
    await deleteVehicleDocument(document.id)
    await reloadDocuments()
  }

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

      <div className="mb-8 grid grid-cols-2 gap-x-8 gap-y-2 rounded-lg border border-border p-4 text-sm md:grid-cols-4">
        <div>
          <p className="text-text-muted">VIN</p>
          <p className="text-text">{vehicle.vin || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Color</p>
          <p className="text-text">{vehicle.color || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Serial del motor</p>
          <p className="text-text">{vehicle.engine_serial || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Capacidad de carga</p>
          <p className="text-text">{vehicle.cargo_capacity_kg != null ? `${vehicle.cargo_capacity_kg} kg` : '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Contrato</p>
          <p className="text-text">{vehicle.contract || '—'}</p>
        </div>
        <div>
          <p className="text-text-muted">Odómetro</p>
          <p className="text-text">
            {vehicle.has_odometer
              ? `Sí${vehicle.odometer_digits ? ` (${vehicle.odometer_digits} dígitos)` : ''}`
              : 'No'}
          </p>
        </div>
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg text-text">Documentos</h2>
        {canWriteVehicle && <Button onClick={() => setShowDocumentModal(true)}>Agregar documento</Button>}
      </div>
      <div className="mb-8">
        <VehicleDocumentsTable documents={documents} canWrite={canWriteVehicle} onDelete={handleDeleteDocument} />
      </div>

      {showDocumentModal && vehicleId && (
        <VehicleDocumentFormModal
          onClose={() => setShowDocumentModal(false)}
          onSubmit={async (values) => {
            await createVehicleDocument(vehicleId, values)
            await reloadDocuments()
          }}
        />
      )}

      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg text-text">Historial de mantenimiento</h2>
        <div className="flex items-center gap-3">
          {canWrite && (
            <Button variant="secondary" onClick={() => setShowSettingsModal(true)}>
              Configurar semáforo
            </Button>
          )}
          {canWrite && <Button onClick={() => setShowTaskModal(true)}>Programar mantenimiento</Button>}
        </div>
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

      {showSettingsModal && (
        <MaintenanceSettingsModal
          onClose={() => setShowSettingsModal(false)}
          onSubmit={async (values) => {
            await updateMaintenanceSettings(values)
            await reload()
          }}
        />
      )}
    </DashboardLayout>
  )
}
