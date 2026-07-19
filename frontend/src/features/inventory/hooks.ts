import { useCallback, useEffect, useState } from 'react'
import { getInventoryItem, listInventoryItems, type InventoryItemListParams } from './api'
import type { Page } from '../../types/common'
import type { InventoryItem, InventoryItemDetail } from '../../types/inventory'

export function useInventoryItems(params: InventoryItemListParams) {
  const [data, setData] = useState<Page<InventoryItem> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listInventoryItems(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar el inventario')
    } finally {
      setIsLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    void reload()
  }, [reload])

  return { data, isLoading, error, reload }
}

export function useInventoryItem(itemId: string | undefined) {
  const [item, setItem] = useState<InventoryItemDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!itemId) return
    setIsLoading(true)
    setItem(await getInventoryItem(itemId))
    setIsLoading(false)
  }, [itemId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { item, isLoading, reload }
}
