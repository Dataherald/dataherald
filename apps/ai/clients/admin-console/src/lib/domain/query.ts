import { capitalize } from '@/lib/utils'
import { EQueryStatus, QueryStatus } from '@/models/api'
import {
  ColorClasses,
  DomainQueryStatus,
  EDomainQueryStatus,
  QueryWorkspaceStatus,
  ResourceButtonClasses,
  ResourceColors,
} from '@/models/domain'

export const QUERY_STATUS_BUTTONS_CLASSES: ResourceButtonClasses<QueryStatus> =
  {
    [EQueryStatus.REJECTED]: 'bg-primary hover:bg-blue-600',
    [EQueryStatus.SQL_ERROR]:
      'border border-primary bg-white text-primary hover:bg-blue-50',
    [EQueryStatus.NOT_VERIFIED]:
      'border border-primary bg-white text-primary hover:bg-blue-50',
    [EQueryStatus.VERIFIED]: 'bg-green-700 hover:bg-green-600',
  }

export const QUERY_STATUS_COLORS: ResourceColors<QueryWorkspaceStatus> = {
  [EQueryStatus.REJECTED]: {
    text: 'text-red-500',
    border: 'border-red-500',
    background: 'bg-red-100',
  },
  [EQueryStatus.NOT_VERIFIED]: {
    text: 'text-gray-500',
    border: 'border-gray-500',
    background: 'bg-gray-100',
  },
  [EQueryStatus.VERIFIED]: {
    text: 'text-green-700',
    border: 'border-green-700',
    background: 'bg-green-100',
  },
}

export const DOMAIN_QUERY_STATUS_COLORS: ResourceColors<DomainQueryStatus> = {
  [EDomainQueryStatus.REJECTED]: {
    text: 'text-red-500',
  },
  [EDomainQueryStatus.SQL_ERROR]: {
    text: 'text-red-500',
  },
  [EDomainQueryStatus.LOW_CONFIDENCE]: {
    text: 'text-orange-600',
  },
  [EDomainQueryStatus.MEDIUM_CONFIDENCE]: {
    text: 'text-yellow-500',
  },
  [EDomainQueryStatus.HIGH_CONFIDENCE]: {
    text: 'text-green-500',
  },
  [EDomainQueryStatus.VERIFIED]: {
    text: 'text-green-700',
  },
}

export const getDomainStatus = (
  status: QueryStatus,
  evaluation_score: number,
): DomainQueryStatus | undefined => {
  switch (status) {
    case EQueryStatus.REJECTED:
      return EDomainQueryStatus.REJECTED
    case EQueryStatus.SQL_ERROR:
      return EDomainQueryStatus.SQL_ERROR
    case EQueryStatus.NOT_VERIFIED: {
      if (evaluation_score < 70) {
        return EDomainQueryStatus.LOW_CONFIDENCE
      } else if (evaluation_score < 90) {
        return EDomainQueryStatus.MEDIUM_CONFIDENCE
      } else {
        return EDomainQueryStatus.HIGH_CONFIDENCE
      }
    }
    case EQueryStatus.VERIFIED:
      return EDomainQueryStatus.VERIFIED
  }
}

export const getDomainStatusColors = (
  status: QueryStatus,
  evaluation_score: number,
): ColorClasses => {
  const domainStatus = getDomainStatus(
    status,
    evaluation_score,
  ) as DomainQueryStatus
  return DOMAIN_QUERY_STATUS_COLORS[domainStatus]
}

export const formatQueryStatus = (
  status?: DomainQueryStatus | QueryStatus,
): string => {
  if (status) {
    const formattedStatus = capitalize(status?.replace('_', ' ').toLowerCase())
    if (status === EQueryStatus.SQL_ERROR) {
      return formattedStatus.replace('Sql', 'SQL')
    }
    return formattedStatus
  }
  return ''
}

export const formatQueryStatusWithScore = (
  status: DomainQueryStatus | QueryStatus | undefined,
  evaluation_score: number,
): string => {
  const formattedStatus = formatQueryStatus(status)
  if (status === EQueryStatus.SQL_ERROR) {
    return formattedStatus
  } else if (status === EQueryStatus.REJECTED) {
    return formattedStatus + ' by Admin'
  } else {
    const formattedScore =
      status === EQueryStatus.VERIFIED ? '(100%)' : `(${evaluation_score}%)`
    return `${formattedStatus} ${formattedScore}`
  }
}

export const isVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.VERIFIED === status

export const isNotVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.NOT_VERIFIED === status

export const isRejected = (status?: QueryStatus): boolean =>
  EQueryStatus.REJECTED === status

export const isSqlError = (status?: QueryStatus): boolean =>
  EQueryStatus.SQL_ERROR === status
