import { useCallback, useEffect, useState } from 'react'
import { listClients, type ClientListParams } from './api'
import type { Page } from '../../types/common'
import type { Client } from '../../types/client'

export function useClients(params: ClientListParams) {
  const [data, setData] = useState<Page<Client> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const page = await listClients(JSON.parse(paramsKey))
      setData(page)
    } catch {
      setError('No se pudo cargar la lista de clientes')
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
