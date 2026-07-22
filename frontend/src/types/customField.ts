export type CustomFieldType = 'texto' | 'numero' | 'fecha' | 'select' | 'checkbox' | 'area_texto'

export const CUSTOM_FIELD_TYPE_LABELS: Record<CustomFieldType, string> = {
  texto: 'Texto',
  numero: 'Número',
  fecha: 'Fecha',
  select: 'Lista de selección',
  checkbox: 'Casilla (sí/no)',
  area_texto: 'Texto largo',
}

export type CustomFieldEntityType =
  | 'vehicle'
  | 'driver'
  | 'trip'
  | 'delivery_order'
  | 'client'
  | 'maintenance_task'
  | 'inventory_item'
  | 'tire'
  | 'delivery_goods'

export const CUSTOM_FIELD_ENTITY_LABELS: Record<CustomFieldEntityType, string> = {
  vehicle: 'Vehículos',
  driver: 'Conductores',
  trip: 'Viajes',
  delivery_order: 'Pedidos de reparto',
  client: 'Clientes',
  maintenance_task: 'Mantenimiento',
  inventory_item: 'Inventario',
  tire: 'Neumáticos',
  delivery_goods: 'Mercancía de reparto',
}

export interface CustomFieldOption {
  value: string
  label: string
}

export interface CustomFieldDefinition {
  id: string
  company_id: string
  entity_type: CustomFieldEntityType
  key: string
  label: string
  field_type: CustomFieldType
  options: CustomFieldOption[]
  required: boolean
  order: number
  active: boolean
  help_text: string | null
  created_at: string
  updated_at: string
}

export type CustomData = Record<string, unknown>
