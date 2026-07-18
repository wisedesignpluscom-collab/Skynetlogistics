import { useCallback, useEffect, useState } from 'react'
import {
  getDriverFatigueHistory,
  getDriverFatigueStatus,
  getDriversFatigueSummary,
  getFatigueRules,
} from './api'
import type { DriverFatigueLog, DriverFatigueSummary, FatigueRule } from '../../types/fatigue'

export function useFatigueRules() {
  const [rule, setRule] = useState<FatigueRule | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setRule(await getFatigueRules())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { rule, isLoading, reload }
}

export function useFatigueSummary() {
  const [summaryByDriver, setSummaryByDriver] = useState<Record<string, DriverFatigueSummary>>({})
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    const items = await getDriversFatigueSummary()
    setSummaryByDriver(Object.fromEntries(items.map((item) => [item.driver_id, item])))
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { summaryByDriver, isLoading, reload }
}

export function useDriverFatigueStatus(driverId: string | null) {
  const [status, setStatus] = useState<DriverFatigueLog | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!driverId) {
      setStatus(null)
      return
    }
    let cancelled = false
    setIsLoading(true)
    getDriverFatigueStatus(driverId)
      .then((result) => {
        if (!cancelled) setStatus(result)
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [driverId])

  return { status, isLoading }
}

export function useDriverFatigueHistory(driverId: string | undefined, dateFrom: string, dateTo: string) {
  const [history, setHistory] = useState<DriverFatigueLog[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!driverId) return
    setIsLoading(true)
    setHistory(await getDriverFatigueHistory(driverId, dateFrom, dateTo))
    setIsLoading(false)
  }, [driverId, dateFrom, dateTo])

  useEffect(() => {
    void reload()
  }, [reload])

  return { history, isLoading, reload }
}
