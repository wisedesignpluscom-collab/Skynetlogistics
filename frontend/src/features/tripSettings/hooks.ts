import { useCallback, useEffect, useState } from 'react'
import {
  listDriverPayRates,
  listExpenseConcepts,
  listHolidays,
  listRateTables,
} from './api'
import type { CompanyHoliday, DriverPayRate, ExpenseConcept, RateTable } from '../../types/tripSettings'

export function useRateTables() {
  const [rateTables, setRateTables] = useState<RateTable[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    const page = await listRateTables()
    setRateTables(page.items)
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { rateTables, isLoading, reload }
}

export function useDriverPayRates() {
  const [rates, setRates] = useState<DriverPayRate[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setRates(await listDriverPayRates())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { rates, isLoading, reload }
}

export function useHolidays() {
  const [holidays, setHolidays] = useState<CompanyHoliday[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setHolidays(await listHolidays())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { holidays, isLoading, reload }
}

export function useExpenseConcepts() {
  const [concepts, setConcepts] = useState<ExpenseConcept[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    const page = await listExpenseConcepts()
    setConcepts(page.items)
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { concepts, isLoading, reload }
}
