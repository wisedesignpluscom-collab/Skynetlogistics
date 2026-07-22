import { useCallback, useEffect, useState } from 'react'
import { listDriverDocumentTypes, listDriverDocuments } from './api'
import type { DriverDocument, DriverDocumentType } from '../../types/driver_document'

export function useDriverDocumentTypes() {
  const [types, setTypes] = useState<DriverDocumentType[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setTypes(await listDriverDocumentTypes())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { types, isLoading, reload }
}

export function useDriverDocuments(driverId: string | undefined) {
  const [documents, setDocuments] = useState<DriverDocument[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!driverId) return
    setIsLoading(true)
    setDocuments(await listDriverDocuments(driverId))
    setIsLoading(false)
  }, [driverId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { documents, isLoading, reload }
}
