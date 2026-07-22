import { useCallback, useEffect, useState } from 'react'
import { listIncidentReports, listMyIncidentReports, type IncidentReportListParams } from './api'
import type { IncidentReport } from '../../types/incident'

export function useIncidentReports(params: IncidentReportListParams) {
  const [items, setItems] = useState<IncidentReport[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const paramsKey = JSON.stringify(params)

  const reload = useCallback(() => {
    setIsLoading(true)
    void listIncidentReports(JSON.parse(paramsKey))
      .then((page) => {
        setItems(page.items)
        setTotal(page.total)
      })
      .finally(() => setIsLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey])

  useEffect(() => {
    reload()
  }, [reload])

  return { items, total, isLoading, reload }
}

export function useMyIncidentReports() {
  const [items, setItems] = useState<IncidentReport[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(() => {
    setIsLoading(true)
    void listMyIncidentReports()
      .then(setItems)
      .finally(() => setIsLoading(false))
  }, [])

  useEffect(() => {
    reload()
  }, [reload])

  return { items, isLoading, reload }
}
