import { useCallback, useEffect, useState } from 'react'
import { listVehicleOwners, type VehicleOwnerListParams } from './api'
import type { Page } from '../../types/common'
import type { VehicleOwner } from '../../types/vehicle_owner'

export function useVehicleOwners(params: VehicleOwnerListParams) {
  const [data, setData] = useState<Page<VehicleOwner> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const page = await listVehicleOwners(JSON.parse(paramsKey))
      setData(page)
    } catch {
      setError('No se pudo cargar la lista de propietarios')
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
