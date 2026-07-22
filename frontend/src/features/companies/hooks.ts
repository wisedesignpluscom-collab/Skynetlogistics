import { useCallback, useEffect, useState } from 'react'
import { listCompanies, type CompanyListParams } from './api'
import type { Page } from '../../types/common'
import type { Company } from '../../types/company'

export function useCompanies(params: CompanyListParams) {
  const [data, setData] = useState<Page<Company> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const page = await listCompanies(JSON.parse(paramsKey))
      setData(page)
    } catch {
      setError('No se pudo cargar la lista de empresas')
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
