import { api } from '../../lib/axios'
import type { DriverFatigueLog, DriverFatigueSummary, FatigueRule } from '../../types/fatigue'

export interface FatigueRuleUpdatePayload {
  max_continuous_hours?: number
  max_24h_hours?: number
  max_7day_hours?: number
  night_driving_weight?: number
  night_start_hour?: number
  night_end_hour?: number
}

export async function getFatigueRules(): Promise<FatigueRule> {
  const { data } = await api.get<FatigueRule>('/fatigue-rules')
  return data
}

export async function updateFatigueRules(payload: FatigueRuleUpdatePayload): Promise<FatigueRule> {
  const { data } = await api.patch<FatigueRule>('/fatigue-rules', payload)
  return data
}

export async function getDriversFatigueSummary(): Promise<DriverFatigueSummary[]> {
  const { data } = await api.get<DriverFatigueSummary[]>('/drivers/fatigue-summary')
  return data
}

export async function getDriverFatigueStatus(driverId: string): Promise<DriverFatigueLog | null> {
  const { data } = await api.get<DriverFatigueLog | null>(`/drivers/${driverId}/fatigue-status`)
  return data
}

export async function getDriverFatigueHistory(
  driverId: string,
  dateFrom: string,
  dateTo: string,
): Promise<DriverFatigueLog[]> {
  const { data } = await api.get<DriverFatigueLog[]>(`/drivers/${driverId}/fatigue-history`, {
    params: { date_from: dateFrom, date_to: dateTo },
  })
  return data
}
