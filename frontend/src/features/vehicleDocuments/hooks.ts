import { useCallback, useEffect, useState } from 'react'
import { listVehicleDocumentTypes, listVehicleDocuments } from './api'
import type { VehicleDocument, VehicleDocumentType } from '../../types/vehicle_document'

export function useVehicleDocumentTypes() {
  const [types, setTypes] = useState<VehicleDocumentType[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    setIsLoading(true)
    setTypes(await listVehicleDocumentTypes())
    setIsLoading(false)
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  return { types, isLoading, reload }
}

export function useVehicleDocuments(vehicleId: string | undefined) {
  const [documents, setDocuments] = useState<VehicleDocument[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const reload = useCallback(async () => {
    if (!vehicleId) return
    setIsLoading(true)
    setDocuments(await listVehicleDocuments(vehicleId))
    setIsLoading(false)
  }, [vehicleId])

  useEffect(() => {
    void reload()
  }, [reload])

  return { documents, isLoading, reload }
}
