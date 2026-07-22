import { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CustomFieldsSection } from '../config/CustomFieldsSection'
import type { DeliveryOrderCreatePayload } from '../../types/delivery'
import type { DeliveryGoods } from '../../types/delivery'
import type { Client } from '../../types/client'
import type { CustomData } from '../../types/customField'

interface LineDraft {
  goods_id: string
  quantity: string
}

export function DeliveryOrderFormModal({
  clients,
  goods,
  onClose,
  onSubmit,
}: {
  clients: Client[]
  goods: DeliveryGoods[]
  onClose: () => void
  onSubmit: (values: DeliveryOrderCreatePayload) => Promise<void>
}) {
  const [clientId, setClientId] = useState(clients[0]?.id ?? '')
  const [address, setAddress] = useState('')
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [notes, setNotes] = useState('')
  const [lines, setLines] = useState<LineDraft[]>([{ goods_id: goods[0]?.id ?? '', quantity: '1' }])
  const [customData, setCustomData] = useState<CustomData>({})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateLine(index: number, patch: Partial<LineDraft>) {
    setLines((prev) => prev.map((l, i) => (i === index ? { ...l, ...patch } : l)))
  }

  async function handleSubmit() {
    if (!clientId) return setError('Selecciona un cliente')
    if (!address.trim()) return setError('Ingresa la dirección de entrega')
    if (!lat || !lng) return setError('Ingresa coordenadas lat/lng')
    const items = lines
      .filter((l) => l.goods_id && Number(l.quantity) > 0)
      .map((l) => ({ goods_id: l.goods_id, quantity: Number(l.quantity) }))
    if (items.length === 0) return setError('Agrega al menos una línea de mercancía')

    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit({
        client_id: clientId,
        address: address.trim(),
        lat: Number(lat),
        lng: Number(lng),
        notes: notes || null,
        custom_data: customData,
        items,
      })
      onClose()
    } catch {
      setError('No se pudo crear el pedido')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title="Nuevo pedido de reparto" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="client">Cliente destinatario</label>
          <select
            id="client"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {clients.length === 0 && <option value="">Sin clientes — crea uno primero</option>}
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <Input id="address" label="Dirección de entrega" value={address} onChange={(e) => setAddress(e.target.value)} />
        <div className="grid grid-cols-2 gap-4">
          <Input id="lat" label="Latitud" type="number" step="any" value={lat} onChange={(e) => setLat(e.target.value)} />
          <Input id="lng" label="Longitud" type="number" step="any" value={lng} onChange={(e) => setLng(e.target.value)} />
        </div>

        <div className="flex flex-col gap-2">
          <p className="text-sm text-text-muted">Mercancía a repartir</p>
          {lines.map((line, i) => (
            <div key={i} className="flex items-end gap-2">
              <div className="flex-1">
                <select
                  value={line.goods_id}
                  onChange={(e) => updateLine(i, { goods_id: e.target.value })}
                  className="w-full rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
                >
                  {goods.length === 0 && <option value="">Sin mercancía en catálogo</option>}
                  {goods.map((g) => (
                    <option key={g.id} value={g.id}>{g.name} ({g.quantity} {g.unit})</option>
                  ))}
                </select>
              </div>
              <input
                type="number"
                step="any"
                min={0}
                value={line.quantity}
                onChange={(e) => updateLine(i, { quantity: e.target.value })}
                className="w-24 rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
              />
              {lines.length > 1 && (
                <button
                  onClick={() => setLines((prev) => prev.filter((_, idx) => idx !== i))}
                  className="px-2 py-2 text-text-muted hover:text-danger"
                  aria-label="Quitar línea"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            onClick={() => setLines((prev) => [...prev, { goods_id: goods[0]?.id ?? '', quantity: '1' }])}
            className="self-start text-sm text-gold hover:underline"
          >
            + Agregar línea
          </button>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="notes">Notas (opcional)</label>
          <textarea
            id="notes"
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          />
        </div>

        <CustomFieldsSection entityType="delivery_order" value={customData} onChange={setCustomData} />

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancelar</Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Crear pedido'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
