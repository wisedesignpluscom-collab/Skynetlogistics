import type { DriverDocument } from '../../types/driver_document'
import { Badge } from '../ui/Badge'

interface DriverDocumentsTableProps {
  documents: DriverDocument[]
  canWrite: boolean
  onDelete: (document: DriverDocument) => void
}

function expiryTone(expiryDate: string | null): 'success' | 'warning' | 'danger' | 'muted' {
  if (!expiryDate) return 'muted'
  const daysLeft = Math.floor((new Date(expiryDate).getTime() - Date.now()) / 86_400_000)
  if (daysLeft <= 0) return 'danger'
  if (daysLeft <= 30) return 'warning'
  return 'success'
}

export function DriverDocumentsTable({ documents, canWrite, onDelete }: DriverDocumentsTableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface text-text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Tipo</th>
            <th className="px-4 py-3 font-medium">Número</th>
            <th className="px-4 py-3 font-medium">Vencimiento</th>
            <th className="px-4 py-3 font-medium">Observaciones</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {documents.map((doc) => (
            <tr key={doc.id} className="bg-background/40">
              <td className="px-4 py-3">{doc.document_type.name}</td>
              <td className="px-4 py-3 text-text-muted">{doc.number || '—'}</td>
              <td className="px-4 py-3">
                {doc.expiry_date ? (
                  <Badge tone={expiryTone(doc.expiry_date)}>{doc.expiry_date}</Badge>
                ) : (
                  <span className="text-text-muted">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-text-muted">{doc.notes || '—'}</td>
              <td className="px-4 py-3 text-right">
                {canWrite && (
                  <button onClick={() => onDelete(doc)} className="text-text-muted hover:text-danger">
                    Eliminar
                  </button>
                )}
              </td>
            </tr>
          ))}
          {documents.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                Este conductor no tiene documentos registrados.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
