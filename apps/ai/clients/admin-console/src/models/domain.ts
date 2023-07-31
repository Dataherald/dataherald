export enum EDomainQueryStatus {
  SQL_ERROR = 'SQL_ERROR',
  LOW_CONFIDENCE = 'LOW_CONFIDENCE',
  MEDIUM_CONFIDENCE = 'MEDIUM_CONFIDENCE',
  HIGH_CONFIDENCE = 'HIGH_CONFIDENCE',
  VERIFIED = 'VERIFIED',
}

export type DomainQueryStatus =
  | 'SQL_ERROR'
  | 'LOW_CONFIDENCE'
  | 'MEDIUM_CONFIDENCE'
  | 'HIGH_CONFIDENCE'
  | 'VERIFIED'

export enum EDomainQueryStatusTextColor {
  SQL_ERROR = 'text-red-500',
  LOW_CONFIDENCE = 'text-orange-600',
  MEDIUM_CONFIDENCE = 'text-yellow-500',
  HIGH_CONFIDENCE = 'text-green-500',
  VERIFIED = 'text-green-700',
}
