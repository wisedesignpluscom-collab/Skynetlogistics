import { useCallback, useEffect, useState } from 'react'
import { listUsers, type UserListParams } from './api'
import type { Page } from '../../types/common'
import type { UserWithRole } from '../../types/user'

export function useUsers(params: UserListParams) {
  const [data, setData] = useState<Page<UserWithRole> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const page = await listUsers(JSON.parse(paramsKey))
      setData(page)
    } catch {
      setError('No se pudo cargar la lista de usuarios')
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
