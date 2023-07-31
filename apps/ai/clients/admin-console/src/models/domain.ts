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

export enum EDomainQueryStatusColor {
  SQL_ERROR = 'red-500',
  LOW_CONFIDENCE = 'orange-600',
  MEDIUM_CONFIDENCE = 'yellow-500',
  HIGH_CONFIDENCE = 'green-500',
  VERIFIED = 'green-700',
}
