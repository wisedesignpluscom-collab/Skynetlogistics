export type InventoryMovementType = 'entrada' | 'salida' | 'ajuste'

export interface InventoryItem {
  id: string
  company_id: string
  warehouse_id: string
  sku: string
  name: string
  unit: string
  quantity: number
  min_stock: number
  unit_cost: number
  custom_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface InventoryMovement {
  id: string
  item_id: string
  vehicle_id: string | null
  provider_id: string | null
  movement_type: InventoryMovementType
  quantity: number
  unit_cost: number | null
  invoice_number: string | null
  tax_percentage: number | null
  reference_doc: string | null
  notes: string | null
  recorded_by: string | null
  created_at: string
}

export interface InventoryItemDetail extends InventoryItem {
  movements: InventoryMovement[]
}
