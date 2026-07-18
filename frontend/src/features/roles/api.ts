import { api } from '../../lib/axios'
import type { Page } from '../../types/common'
import type { Role } from '../../types/role'

export async function listRoles(): Promise<Page<Role>> {
  const { data } = await api.get<Page<Role>>('/roles', { params: { page_size: 100 } })
  return data
}
