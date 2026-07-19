import { useCallback, useEffect, useState } from 'react'
import { getTripRoute } from './api'
import type { RoutePlanDetail } from '../../types/route'

export function useTripRoute(tripId: string | undefined) {
  const [plan, setPlan] = useState<RoutePlanDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!tripId) return
    setIsLoading(true)
    try {
      setPlan(await getTripRoute(tripId))
    } finally {
      setIsLoading(false)
    }
  }, [tripId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { plan, isLoading, reload }
}
