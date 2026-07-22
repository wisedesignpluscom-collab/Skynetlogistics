import { useCallback, useEffect, useState } from 'react'
import { getAvailableVehicles } from './api'
import type { Vehicle } from '../../types/vehicle'

export function useAvailableVehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    try {
      setVehicles(await getAvailableVehicles())
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { vehicles, isLoading, reload }
}
