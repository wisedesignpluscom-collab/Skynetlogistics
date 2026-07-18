import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Provider } from '../../types/provider'

export async function listProviders(): Promise<Page<Provider>> {
  const { data } = await api.get<Page<Provider>>('/providers', { params: { page_size: 100 } })
  return data
}
