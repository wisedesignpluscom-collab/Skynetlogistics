import { useEffect, useState } from 'react'
import { listProviders } from './api'
import type { Provider } from '../../types/provider'

export function useProviders() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    listProviders()
      .then((page) => setProviders(page.items))
      .finally(() => setIsLoading(false))
  }, [])

  return { providers, isLoading }
}
