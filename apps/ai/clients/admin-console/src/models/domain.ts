export enum EDomainQueryStatus {
  REJECTED = 'REJECTED',
  SQL_ERROR = 'SQL_ERROR',
  LOW_CONFIDENCE = 'LOW_CONFIDENCE',
  MEDIUM_CONFIDENCE = 'MEDIUM_CONFIDENCE',
  HIGH_CONFIDENCE = 'HIGH_CONFIDENCE',
  VERIFIED = 'VERIFIED',
}

export type DomainQueryStatus =
  | 'REJECTED'
  | 'SQL_ERROR'
  | 'LOW_CONFIDENCE'
  | 'MEDIUM_CONFIDENCE'
  | 'HIGH_CONFIDENCE'
  | 'VERIFIED'

export type ColorClasses = {
  text?: string
  border?: string
  background?: string
}

export type ResourceColors<T extends string> = Record<T, ColorClasses>
