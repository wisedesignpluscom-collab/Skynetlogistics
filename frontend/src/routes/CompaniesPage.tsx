import { useState } from 'react'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { CompanyTable } from '../components/companies/CompanyTable'
import { CompanyFormModal } from '../components/companies/CompanyFormModal'
import { useCompanies } from '../features/companies/hooks'
import { createCompany, deactivateCompany, updateCompany } from '../features/companies/api'
import { useAuth } from '../features/auth/AuthContext'
import type { Company } from '../types/company'
import type { CompanyPayload } from '../features/companies/api'

type ModalState = { mode: 'create' } | { mode: 'edit'; company: Company } | null

export function CompaniesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const { data, isLoading, error, reload } = useCompanies({ search: search || undefined, page_size: 50 })
  const [modalState, setModalState] = useState<ModalState>(null)

  if (!user?.is_superadmin) {
    return (
      <DashboardLayout>
        <p className="text-text-muted">No tienes acceso a esta sección.</p>
      </DashboardLayout>
    )
  }

  async function handleDeactivate(company: Company) {
    if (!window.confirm(`¿Desactivar la empresa ${company.name}?`)) return
    await deactivateCompany(company.id)
    await reload()
  }

  async function handleSubmit(values: CompanyPayload) {
    if (modalState?.mode === 'create') {
      await createCompany(values)
    } else if (modalState?.mode === 'edit') {
      await updateCompany(modalState.company.id, values)
    }
    await reload()
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-text">Empresas</h1>
        <Button onClick={() => setModalState({ mode: 'create' })}>Nueva empresa</Button>
      </div>

      <div className="mb-4 max-w-xs">
        <Input
          placeholder="Buscar por nombre…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading && <p className="text-text-muted">Cargando…</p>}
      {error && <p className="text-danger">{error}</p>}
      {data && (
        <CompanyTable
          companies={data.items}
          canWrite
          canDelete
          onEdit={(company) => setModalState({ mode: 'edit', company })}
          onDeactivate={handleDeactivate}
        />
      )}

      {modalState && (
        <CompanyFormModal
          mode={modalState.mode}
          initialCompany={modalState.mode === 'edit' ? modalState.company : undefined}
          onClose={() => setModalState(null)}
          onSubmit={handleSubmit}
        />
      )}
    </DashboardLayout>
  )
}
