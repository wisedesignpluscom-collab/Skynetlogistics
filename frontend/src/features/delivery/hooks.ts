import { useCallback, useEffect, useState } from 'react'
import { getDeliveryGoods, listDeliveryGoods, type DeliveryGoodsListParams } from './api'
import type { Page } from '../../types/common'
import type { DeliveryGoods, DeliveryGoodsDetail } from '../../types/delivery'

export function useDeliveryGoods(params: DeliveryGoodsListParams) {
  const [data, setData] = useState<Page<DeliveryGoods> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listDeliveryGoods(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar la mercancía de reparto')
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

export function useDeliveryGoodsDetail(goodsId: string | undefined) {
  const [goods, setGoods] = useState<DeliveryGoodsDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!goodsId) return
    setIsLoading(true)
    setGoods(await getDeliveryGoods(goodsId))
    setIsLoading(false)
  }, [goodsId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { goods, isLoading, reload }
}
