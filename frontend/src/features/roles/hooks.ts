import { useEffect, useState } from 'react'
import { listRoles } from './api'
import type { Role } from '../../types/role'

export function useRoles() {
  const [roles, setRoles] = useState<Role[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    listRoles()
      .then((page) => setRoles(page.items))
      .finally(() => setIsLoading(false))
  }, [])

  return { roles, isLoading }
}
