import { useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { GPSProviderFormModal } from '../components/gps/GPSProviderFormModal'
import { WebhookTokenModal } from '../components/gps/WebhookTokenModal'
import { VehicleMapSection } from '../components/gps/VehicleMapSection'
import { useGpsProviders } from '../features/gps/hooks'
import { createGpsProvider, deleteGpsProvider, regenerateWebhookToken } from '../features/gps/api'
import { useAuth } from '../features/auth/AuthContext'

export function GPSSettingsPage() {
  const { hasPermission } = useAuth()
  const { providers, isLoading, reload } = useGpsProviders()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [tokenModal, setTokenModal] = useState<{ providerId: string; token: string } | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const canWrite = hasPermission('gps', 'write')
  const canDelete = hasPermission('gps', 'delete')

  async function handleDelete(id: string) {
    if (!window.confirm('¿Eliminar este proveedor GPS? Se perderá el mapeo de vehículos asociado.')) return
    await deleteGpsProvider(id)
    await reload()
  }

  async function handleRegenerate(id: string) {
    const result = await regenerateWebhookToken(id)
    if (result.webhook_token) {
      setTokenModal({ providerId: id, token: result.webhook_token })
    }
  }

  return (
    <DashboardLayout>
      <Link to="/gps-map" className="text-sm text-text-muted hover:text-gold">
        ← Volver al mapa
      </Link>
      <div className="mt-4 mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Proveedores GPS</h1>
        {canWrite && <Button onClick={() => setShowCreateModal(true)}>Nuevo proveedor</Button>}
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}

      <div className="flex flex-col gap-4">
        {providers.map((provider) => (
          <div key={provider.id} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-display text-lg text-text">{provider.provider_name}</p>
                <p className="text-sm text-text-muted">
                  {provider.adapter_type} · {provider.ingestion_mode}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone={provider.is_active ? 'gold' : 'muted'}>
                  {provider.is_active ? 'activo' : 'inactivo'}
                </Badge>
                {canWrite && provider.ingestion_mode === 'webhook' && (
                  <button
                    onClick={() => handleRegenerate(provider.id)}
                    className="text-sm text-text-muted hover:text-gold"
                  >
                    Regenerar token
                  </button>
                )}
                {canDelete && (
                  <button
                    onClick={() => handleDelete(provider.id)}
                    className="text-sm text-text-muted hover:text-danger"
                  >
                    Eliminar
                  </button>
                )}
                <button
                  onClick={() => setExpandedId(expandedId === provider.id ? null : provider.id)}
                  className="text-sm text-text-muted hover:text-text"
                >
                  {expandedId === provider.id ? 'Ocultar' : 'Vehículos'}
                </button>
              </div>
            </div>

            {expandedId === provider.id && (
              <VehicleMapSection providerId={provider.id} canWrite={canWrite} />
            )}
          </div>
        ))}
        {!isLoading && providers.length === 0 && (
          <p className="text-text-muted">No hay proveedores GPS configurados.</p>
        )}
      </div>

      {showCreateModal && (
        <GPSProviderFormModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={async (values) => {
            const created = await createGpsProvider(values)
            await reload()
            if (created.webhook_token) {
              setTokenModal({ providerId: created.id, token: created.webhook_token })
            }
          }}
        />
      )}

      {tokenModal && (
        <WebhookTokenModal
          providerId={tokenModal.providerId}
          token={tokenModal.token}
          onClose={() => setTokenModal(null)}
        />
      )}
    </DashboardLayout>
  )
}
