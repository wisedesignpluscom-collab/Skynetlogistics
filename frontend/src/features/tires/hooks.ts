import { useCallback, useEffect, useState } from 'react'
import {
  getTire,
  getTirePerformance,
  getTireSettings,
  getVehicleTires,
  listTires,
  listWarehouses,
  type TireListParams,
} from './api'
import type { Page } from '../../types/common'
import type { Tire, TireDetail, TirePerformanceRow, TireSettings, Warehouse } from '../../types/tire'

export function useTires(params: TireListParams) {
  const [data, setData] = useState<Page<Tire> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      setData(await listTires(JSON.parse(paramsKey)))
    } catch {
      setError('No se pudo cargar la lista de neumáticos')
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

export function useTire(tireId: string | undefined) {
  const [tire, setTire] = useState<TireDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!tireId) return
    setIsLoading(true)
    setTire(await getTire(tireId))
    setIsLoading(false)
  }, [tireId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { tire, isLoading, reload }
}

export function useVehicleTires(vehicleId: string | undefined) {
  const [tires, setTires] = useState<Tire[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!vehicleId) return
    setIsLoading(true)
    setTires(await getVehicleTires(vehicleId))
    setIsLoading(false)
  }, [vehicleId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { tires, isLoading, reload }
}

export function useWarehouses() {
  const [data, setData] = useState<Page<Warehouse> | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setData(await listWarehouses({ page_size: 100 }))
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { data, isLoading, reload }
}

export function useTireSettings() {
  const [settings, setSettings] = useState<TireSettings | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setSettings(await getTireSettings())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { settings, isLoading, reload }
}

export function useTirePerformance() {
  const [rows, setRows] = useState<TirePerformanceRow[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setRows(await getTirePerformance())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { rows, isLoading, reload }
}
