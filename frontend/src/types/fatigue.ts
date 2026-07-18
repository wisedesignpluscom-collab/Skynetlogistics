export type FatigueRiskLevel = 'bajo' | 'medio' | 'alto' | 'critico'

export interface FatigueRule {
  id: string
  company_id: string
  max_continuous_hours: number
  max_24h_hours: number
  max_7day_hours: number
  night_driving_weight: number
  night_start_hour: number
  night_end_hour: number
  created_at: string
  updated_at: string
}

export interface DriverFatigueLog {
  id: string
  driver_id: string
  date: string
  continuous_driving_min: number
  total_24h_min: number
  total_7day_min: number
  night_driving_min: number
  risk_score: number
  risk_level: FatigueRiskLevel
  computed_at: string
}

export interface DriverFatigueSummary {
  driver_id: string
  risk_level: FatigueRiskLevel | null
  risk_score: number | null
  computed_at: string | null
}
