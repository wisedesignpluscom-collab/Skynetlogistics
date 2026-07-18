import { useCallback, useEffect, useState } from 'react'
import { listTrips, type TripListParams } from './api'
import type { Page } from '../../types/common'
import type { Trip } from '../../types/trip'

export function useTrips(params: TripListParams) {
  const [data, setData] = useState<Page<Trip> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listTrips(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar la lista de viajes')
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
