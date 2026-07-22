import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { API_ORIGIN } from '../../lib/axios'

interface WebhookTokenModalProps {
  providerId: string
  token: string
  onClose: () => void
}

export function WebhookTokenModal({ providerId, token, onClose }: WebhookTokenModalProps) {
  const webhookUrl = `${API_ORIGIN || window.location.origin}/api/v1/gps/webhook/${providerId}`

  return (
    <Modal title="Token del webhook" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-danger">
          Guarda este token ahora — no se puede volver a mostrar. Si lo pierdes, tendrás que regenerarlo.
        </p>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted">URL del webhook</label>
          <code className="break-all rounded-md border border-border bg-surface px-3 py-2 text-sm text-text">
            {webhookUrl}
          </code>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted">Header requerido</label>
          <code className="break-all rounded-md border border-border bg-surface px-3 py-2 text-sm text-text">
            X-Webhook-Token: {token}
          </code>
        </div>
        <div className="mt-2 flex justify-end">
          <Button onClick={onClose}>Entendido</Button>
        </div>
      </div>
    </Modal>
  )
}
