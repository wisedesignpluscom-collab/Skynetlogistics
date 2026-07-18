import { useCallback, useEffect, useState } from 'react'
import { listVehicles, type VehicleListParams } from './api'
import type { Page } from '../../types/common'
import type { Vehicle } from '../../types/vehicle'

export function useVehicles(params: VehicleListParams) {
  const [data, setData] = useState<Page<Vehicle> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listVehicles(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar la lista de vehículos')
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
