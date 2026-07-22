import { useCallback, useEffect, useState } from 'react'
import { listCustomFields } from './api'
import type { CustomFieldDefinition, CustomFieldEntityType } from '../../types/customField'

/** Campos custom de una entidad. `onlyActive` para los formularios (render); false para la
 *  pantalla de administración (muestra también los desactivados). */
export function useCustomFields(entityType: CustomFieldEntityType | undefined, onlyActive = false) {
  const [fields, setFields] = useState<CustomFieldDefinition[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!entityType) return
    setIsLoading(true)
    try {
      setFields(await listCustomFields(entityType, onlyActive))
    } finally {
      setIsLoading(false)
    }
  }, [entityType, onlyActive])

  useEffect(() => {
    void reload()
  }, [reload])

  return { fields, isLoading, reload }
}
