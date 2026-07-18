import { useCallback, useEffect, useState } from 'react'
import { listDrivers, type DriverListParams } from './api'
import type { Page } from '../../types/common'
import type { Driver } from '../../types/driver'

export function useDrivers(params: DriverListParams) {
  const [data, setData] = useState<Page<Driver> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listDrivers(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar la lista de conductores')
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
