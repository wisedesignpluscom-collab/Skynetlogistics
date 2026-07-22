import type { Company } from '../../types/company'
import { Badge } from '../ui/Badge'

interface CompanyTableProps {
  companies: Company[]
  canWrite: boolean
  canDelete: boolean
  onEdit: (company: Company) => void
  onDeactivate: (company: Company) => void
}

export function CompanyTable({ companies, canWrite, canDelete, onEdit, onDeactivate }: CompanyTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">RIF / Tax ID</th>
            <th className="px-4 py-3 font-medium">Contacto</th>
            <th className="px-4 py-3 font-medium">Ubicación</th>
            <th className="px-4 py-3 font-medium">Plan</th>
            <th className="px-4 py-3 font-medium">Estado</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {companies.map((company) => (
            <tr key={company.id} className="bg-background/40">
              <td className="px-4 py-3">{company.name}</td>
              <td className="px-4 py-3 text-text-muted">{company.tax_id}</td>
              <td className="px-4 py-3 text-text-muted">
                {company.contact_person || '—'}
                {company.phone && <div className="text-xs">{company.phone}</div>}
              </td>
              <td className="px-4 py-3 text-text-muted">
                {[company.city, company.state, company.country].filter(Boolean).join(', ') || '—'}
              </td>
              <td className="px-4 py-3">
                <Badge tone="gold">{company.plan}</Badge>
              </td>
              <td className="px-4 py-3">
                <Badge tone={company.is_active ? 'gold' : 'muted'}>
                  {company.is_active ? 'Activa' : 'Inactiva'}
                </Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-3">
                  {canWrite && (
                    <button onClick={() => onEdit(company)} className="text-text-muted hover:text-gold">
                      Editar
                    </button>
                  )}
                  {canDelete && company.is_active && (
                    <button
                      onClick={() => onDeactivate(company)}
                      className="text-text-muted hover:text-danger"
                    >
                      Desactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {companies.length === 0 && (
            <tr>
              <td colSpan={7} className="px-4 py-8 text-center text-text-muted">
                No hay empresas para mostrar.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
