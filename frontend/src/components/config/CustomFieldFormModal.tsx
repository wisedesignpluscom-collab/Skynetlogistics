import { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { CUSTOM_FIELD_TYPE_LABELS } from '../../types/customField'
import type {
  CustomFieldDefinition,
  CustomFieldEntityType,
  CustomFieldOption,
  CustomFieldType,
} from '../../types/customField'
import type { CustomFieldCreatePayload, CustomFieldUpdatePayload } from '../../features/config/api'

const TYPES = Object.keys(CUSTOM_FIELD_TYPE_LABELS) as CustomFieldType[]

function slugify(label: string): string {
  return label
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/^[0-9]/, 'c$&')
}

export function CustomFieldFormModal({
  entityType,
  existing,
  onClose,
  onCreate,
  onUpdate,
}: {
  entityType: CustomFieldEntityType
  existing: CustomFieldDefinition | null
  onClose: () => void
  onCreate: (payload: CustomFieldCreatePayload) => Promise<void>
  onUpdate: (id: string, payload: CustomFieldUpdatePayload) => Promise<void>
}) {
  const isEdit = existing !== null
  const [label, setLabel] = useState(existing?.label ?? '')
  const [fieldType, setFieldType] = useState<CustomFieldType>(existing?.field_type ?? 'texto')
  const [required, setRequired] = useState(existing?.required ?? false)
  const [helpText, setHelpText] = useState(existing?.help_text ?? '')
  const [options, setOptions] = useState<CustomFieldOption[]>(existing?.options ?? [])
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateOption(i: number, patch: Partial<CustomFieldOption>) {
    setOptions((prev) => prev.map((o, idx) => (idx === i ? { ...o, ...patch } : o)))
  }

  async function handleSubmit() {
    if (!label.trim()) return setError('El nombre es obligatorio')
    const cleanOptions = options
      .filter((o) => o.value.trim() && o.label.trim())
      .map((o) => ({ value: o.value.trim(), label: o.label.trim() }))
    if (fieldType === 'select' && cleanOptions.length === 0) {
      return setError('Una lista de selección necesita al menos una opción')
    }
    setIsSubmitting(true)
    setError(null)
    try {
      if (isEdit) {
        await onUpdate(existing.id, {
          label: label.trim(),
          required,
          help_text: helpText || null,
          options: cleanOptions,
        })
      } else {
        await onCreate({
          entity_type: entityType,
          key: slugify(label),
          label: label.trim(),
          field_type: fieldType,
          required,
          help_text: helpText || null,
          options: cleanOptions,
        })
      }
      onClose()
    } catch {
      setError('No se pudo guardar (¿clave duplicada?)')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal title={isEdit ? `Editar «${existing.label}»` : 'Nuevo campo'} onClose={onClose}>
      <div className="flex flex-col gap-4">
        <Input id="label" label="Nombre del campo" value={label} onChange={(e) => setLabel(e.target.value)} />

        <div className="flex flex-col gap-1">
          <label className="text-sm text-text-muted" htmlFor="type">Tipo</label>
          <select
            id="type"
            value={fieldType}
            disabled={isEdit}
            onChange={(e) => setFieldType(e.target.value as CustomFieldType)}
            className="rounded-md border border-border bg-surface px-3 py-2 text-text disabled:opacity-60 focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
          >
            {TYPES.map((t) => (
              <option key={t} value={t}>{CUSTOM_FIELD_TYPE_LABELS[t]}</option>
            ))}
          </select>
          {isEdit && <span className="text-xs text-text-muted">El tipo no se puede cambiar tras crear.</span>}
        </div>

        {fieldType === 'select' && (
          <div className="flex flex-col gap-2">
            <p className="text-sm text-text-muted">Opciones de la lista</p>
            {options.map((o, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  placeholder="valor"
                  value={o.value}
                  onChange={(e) => updateOption(i, { value: e.target.value })}
                  className="w-1/3 rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus:border-gold focus:outline-none"
                />
                <input
                  placeholder="etiqueta visible"
                  value={o.label}
                  onChange={(e) => updateOption(i, { label: e.target.value })}
                  className="flex-1 rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus:border-gold focus:outline-none"
                />
                <button onClick={() => setOptions((p) => p.filter((_, idx) => idx !== i))} className="text-text-muted hover:text-danger">✕</button>
              </div>
            ))}
            <button
              onClick={() => setOptions((p) => [...p, { value: '', label: '' }])}
              className="self-start text-sm text-gold hover:underline"
            >
              + Agregar opción
            </button>
          </div>
        )}

        <label className="flex items-center gap-2 text-sm text-text">
          <input type="checkbox" checked={required} onChange={(e) => setRequired(e.target.checked)} />
          Obligatorio
        </label>

        <Input id="help" label="Texto de ayuda (opcional)" value={helpText} onChange={(e) => setHelpText(e.target.value)} />

        {error && <p className="text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancelar</Button>
          <Button onClick={() => void handleSubmit()} disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : isEdit ? 'Guardar' : 'Crear'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
