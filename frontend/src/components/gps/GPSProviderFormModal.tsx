import { useState, type FormEvent } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import type { IngestionMode } from '../../types/gps'
import type { GPSProviderPayload } from '../../features/gps/api'

interface GPSProviderFormModalProps {
  onClose: () => void
  onSubmit: (values: GPSProviderPayload) => Promise<void>
}

export function GPSProviderFormModal({ onClose, onSubmit }: GPSProviderFormModalProps) {
  const [providerName, setProviderName] = useState('')
  const [adapterType, setAdapterType] = useState('traker_gps')
  const [ingestionMode, setIngestionMode] = useState<IngestionMode>('webhook')
  const [apiKey, setApiKey] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({
        provider_name: providerName,
        adapter_type: adapterType,
        api_credentials: { api_key: apiKey },
        ingestion_mode: ingestionMode,
      })
      onClose()
    } catch {
      setError('No se pudo crear el proveedor GPS')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo proveedor GPS" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          id="provider_name"
          label="Nombre del proveedor"
          value={providerName}
          onChange={(e) => setProviderName(e.target.value)}
          required
        />
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="adapter_type">
            Tipo de adaptador
          </label>
          <select
            id="adapter_type"
            value={adapterType}
            onChange={(e) => setAdapterType(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="traker_gps">Traker GPS</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="ingestion_mode">
            Modo de ingesta
          </label>
          <select
            id="ingestion_mode"
            value={ingestionMode}
            onChange={(e) => setIngestionMode(e.target.value as IngestionMode)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            <option value="webhook">Webhook (el proveedor empuja los datos)</option>
            <option value="polling">Polling (nosotros consultamos periódicamente)</option>
          </select>
        </div>
        <Input
          id="api_key"
          label="API key / credencial del proveedor"
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
        />

        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creando…' : 'Crear proveedor'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
