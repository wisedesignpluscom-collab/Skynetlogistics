import { useState } from 'react'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { CustomFieldsAdmin } from '../components/config/CustomFieldsAdmin'
import { FormRulesAdmin } from '../components/config/FormRulesAdmin'
import { WorkflowsAdmin } from '../components/config/WorkflowsAdmin'
import { CUSTOM_FIELD_ENTITY_LABELS } from '../types/customField'
import type { CustomFieldEntityType } from '../types/customField'

const ENTITIES = Object.keys(CUSTOM_FIELD_ENTITY_LABELS) as CustomFieldEntityType[]
type Tab = 'campos' | 'reglas' | 'workflows'

export function ConfigPage() {
  const [entity, setEntity] = useState<CustomFieldEntityType>('vehicle')
  const [tab, setTab] = useState<Tab>('campos')

  return (
    <DashboardLayout>
      <h1 className="mb-2 font-display text-2xl text-text">Configuración</h1>
      <p className="mb-6 text-sm text-text-muted">
        Adapta los formularios del sistema a tu operación: campos personalizados y reglas sin código.
      </p>

      <div className="mb-4 flex flex-col gap-1">
        <label className="text-sm text-text-muted" htmlFor="entity">Formulario</label>
        <select
          id="entity"
          value={entity}
          onChange={(e) => setEntity(e.target.value as CustomFieldEntityType)}
          className="max-w-xs rounded-md border border-border bg-surface px-3 py-2 text-text focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold"
        >
          {ENTITIES.map((en) => (
            <option key={en} value={en}>{CUSTOM_FIELD_ENTITY_LABELS[en]}</option>
          ))}
        </select>
      </div>

      <div className="mb-6 inline-flex rounded-lg border border-border bg-surface p-1">
        <button
          onClick={() => setTab('campos')}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${tab === 'campos' ? 'bg-gold text-white' : 'text-text-muted hover:text-text'}`}
        >
          Campos personalizados
        </button>
        <button
          onClick={() => setTab('reglas')}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${tab === 'reglas' ? 'bg-gold text-white' : 'text-text-muted hover:text-text'}`}
        >
          Reglas
        </button>
        <button
          onClick={() => setTab('workflows')}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${tab === 'workflows' ? 'bg-gold text-white' : 'text-text-muted hover:text-text'}`}
        >
          Workflows
        </button>
      </div>

      {tab === 'campos' && <CustomFieldsAdmin entity={entity} />}
      {tab === 'reglas' && <FormRulesAdmin entity={entity} />}
      {tab === 'workflows' && <WorkflowsAdmin entity={entity} />}
    </DashboardLayout>
  )
}
