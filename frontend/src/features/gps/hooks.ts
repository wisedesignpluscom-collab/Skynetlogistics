import { useCallback, useEffect, useState } from 'react'
import { getFleetLatestPositions, listGpsProviders } from './api'
import type { GPSProvider, VehiclePosition } from '../../types/gps'

export function useGpsProviders() {
  const [providers, setProviders] = useState<GPSProvider[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setProviders(await listGpsProviders())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { providers, isLoading, reload }
}

export function useFleetPositions(pollIntervalMs = 15000) {
  const [positions, setPositions] = useState<VehiclePosition[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setPositions(await getFleetLatestPositions())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
    const interval = setInterval(() => void reload(), pollIntervalMs)
    return () => clearInterval(interval)
  }, [reload, pollIntervalMs])

  return { positions, isLoading, reload }
}
