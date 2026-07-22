export type DeliveryGoodsMovementType = 'entrada' | 'salida' | 'ajuste'

export interface DeliveryGoods {
  id: string
  company_id: string
  warehouse_id: string
  sku: string
  name: string
  unit: string
  quantity: number
  min_stock: number
  unit_cost: number
  weight_kg_per_unit: number
  volume_m3_per_unit: number
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface DeliveryGoodsMovement {
  id: string
  goods_id: string
  movement_type: DeliveryGoodsMovementType
  quantity: number
  unit_cost: number | null
  reference_doc: string | null
  notes: string | null
  recorded_by: string | null
  created_at: string
}

export interface DeliveryGoodsDetail extends DeliveryGoods {
  movements: DeliveryGoodsMovement[]
}

export type DeliveryOrderStatus = 'pendiente' | 'asignado' | 'en_ruta' | 'entregado' | 'fallido'

export const DELIVERY_ORDER_STATUS_LABELS: Record<DeliveryOrderStatus, string> = {
  pendiente: 'Pendiente',
  asignado: 'Asignado',
  en_ruta: 'En ruta',
  entregado: 'Entregado',
  fallido: 'Fallido',
}

export interface DeliveryOrderItem {
  id: string
  goods_id: string
  quantity: number
}

export interface DeliveryOrder {
  id: string
  company_id: string
  client_id: string
  trip_id: string | null
  address: string
  lat: number
  lng: number
  status: DeliveryOrderStatus
  priority: number
  time_window_start: string | null
  time_window_end: string | null
  notes: string | null
  delivered_at: string | null
  delivered_by: string | null
  delivery_proof_url: string | null
  failure_reason: string | null
  created_by: string | null
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
  items: DeliveryOrderItem[]
}

export interface DeliveryOrderItemInput {
  goods_id: string
  quantity: number
}

export interface DeliveryOrderCreatePayload {
  client_id: string
  address: string
  lat: number
  lng: number
  priority?: number
  notes?: string | null
  custom_data?: Record<string, unknown>
  items: DeliveryOrderItemInput[]
}
