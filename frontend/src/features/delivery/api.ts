import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type {
  DeliveryGoods,
  DeliveryGoodsDetail,
  DeliveryGoodsMovement,
  DeliveryGoodsMovementType,
  DeliveryOrder,
  DeliveryOrderCreatePayload,
  DeliveryOrderStatus,
} from '../../types/delivery'

export interface DeliveryGoodsListParams {
  page?: number
  page_size?: number
  warehouse_id?: string
  search?: string
  low_stock?: boolean
}

export interface DeliveryGoodsCreatePayload {
  warehouse_id: string
  sku: string
  name: string
  unit: string
  min_stock?: number
  unit_cost?: number
  weight_kg_per_unit?: number
  volume_m3_per_unit?: number
  custom_data?: Record<string, unknown>
}

export interface DeliveryGoodsMovementPayload {
  goods_id: string
  movement_type: DeliveryGoodsMovementType
  quantity: number
  unit_cost?: number | null
  reference_doc?: string | null
  notes?: string | null
}

export async function listDeliveryGoods(params: DeliveryGoodsListParams = {}): Promise<Page<DeliveryGoods>> {
  const { data } = await api.get<Page<DeliveryGoods>>('/delivery-goods', { params })
  return data
}

export async function getDeliveryGoods(id: string): Promise<DeliveryGoodsDetail> {
  const { data } = await api.get<DeliveryGoodsDetail>(`/delivery-goods/${id}`)
  return data
}

export async function createDeliveryGoods(payload: DeliveryGoodsCreatePayload): Promise<DeliveryGoods> {
  const { data } = await api.post<DeliveryGoods>('/delivery-goods', payload)
  return data
}

export async function createDeliveryGoodsMovement(payload: DeliveryGoodsMovementPayload): Promise<DeliveryGoodsMovement> {
  const { data } = await api.post<DeliveryGoodsMovement>('/delivery-goods/movements', payload)
  return data
}

// --- Pedidos de reparto (9B) ---

export interface DeliveryOrderListParams {
  page?: number
  page_size?: number
  status_filter?: DeliveryOrderStatus
  trip_id?: string
  client_id?: string
}

export async function listDeliveryOrders(params: DeliveryOrderListParams = {}): Promise<Page<DeliveryOrder>> {
  const { data } = await api.get<Page<DeliveryOrder>>('/delivery-orders', { params })
  return data
}

export async function getDeliveryOrder(id: string): Promise<DeliveryOrder> {
  const { data } = await api.get<DeliveryOrder>(`/delivery-orders/${id}`)
  return data
}

export async function createDeliveryOrder(payload: DeliveryOrderCreatePayload): Promise<DeliveryOrder> {
  const { data } = await api.post<DeliveryOrder>('/delivery-orders', payload)
  return data
}

export async function assignDeliveryOrder(id: string, tripId: string): Promise<DeliveryOrder> {
  const { data } = await api.post<DeliveryOrder>(`/delivery-orders/${id}/assign`, { trip_id: tripId })
  return data
}

export async function listMyDeliveryOrders(): Promise<DeliveryOrder[]> {
  const { data } = await api.get<DeliveryOrder[]>('/delivery-orders/mine')
  return data
}

export async function deliverDeliveryOrder(id: string, notes?: string): Promise<DeliveryOrder> {
  const { data } = await api.post<DeliveryOrder>(`/delivery-orders/${id}/deliver`, { notes: notes ?? null })
  return data
}

export async function failDeliveryOrder(id: string, failureReason: string, returnStock = true): Promise<DeliveryOrder> {
  const { data } = await api.post<DeliveryOrder>(`/delivery-orders/${id}/fail`, {
    failure_reason: failureReason,
    return_stock: returnStock,
  })
  return data
}
