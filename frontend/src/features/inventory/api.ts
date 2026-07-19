import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { InventoryItem, InventoryItemDetail, InventoryMovement, InventoryMovementType } from '../../types/inventory'

export interface InventoryItemListParams {
  page?: number
  page_size?: number
  warehouse_id?: string
  search?: string
  low_stock?: boolean
}

export interface InventoryItemCreatePayload {
  warehouse_id: string
  sku: string
  name: string
  unit: string
  min_stock?: number
  unit_cost?: number
}

export interface InventoryItemUpdatePayload {
  warehouse_id?: string
  name?: string
  unit?: string
  min_stock?: number
  unit_cost?: number
}

export interface InventoryMovementPayload {
  item_id: string
  movement_type: InventoryMovementType
  quantity: number
  vehicle_id?: string | null
  unit_cost?: number | null
  reference_doc?: string | null
  notes?: string | null
}

export async function listInventoryItems(params: InventoryItemListParams = {}): Promise<Page<InventoryItem>> {
  const { data } = await api.get<Page<InventoryItem>>('/inventory-items', { params })
  return data
}

export async function getInventoryItem(id: string): Promise<InventoryItemDetail> {
  const { data } = await api.get<InventoryItemDetail>(`/inventory-items/${id}`)
  return data
}

export async function createInventoryItem(payload: InventoryItemCreatePayload): Promise<InventoryItem> {
  const { data } = await api.post<InventoryItem>('/inventory-items', payload)
  return data
}

export async function updateInventoryItem(id: string, payload: InventoryItemUpdatePayload): Promise<InventoryItem> {
  const { data } = await api.patch<InventoryItem>(`/inventory-items/${id}`, payload)
  return data
}

export async function createInventoryMovement(payload: InventoryMovementPayload): Promise<InventoryMovement> {
  const { data } = await api.post<InventoryMovement>('/inventory-movements', payload)
  return data
}

export async function listInventoryMovements(params: { item_id?: string; vehicle_id?: string }): Promise<InventoryMovement[]> {
  const { data } = await api.get<InventoryMovement[]>('/inventory-movements', { params })
  return data
}
