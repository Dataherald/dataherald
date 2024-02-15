import { capitalize } from '@/lib/utils'
import { EQueryStatus, Query, QueryListItem, QueryStatus } from '@/models/api'
import {
  ColorClasses,
  DomainQueryStatus,
  EDomainQueryConfidence,
  EDomainQueryStatus,
  QueryWorkspaceStatus,
  ResourceColors,
} from '@/models/domain'

export const mapQuery = <T extends Query | QueryListItem>({
  confidence_score,
  ...props
}: T): T =>
  ({
    ...props,
    confidence_score: confidence_score !== null ? confidence_score * 100 : null,
  } as T)

export const QUERY_STATUS_COLORS: ResourceColors<QueryWorkspaceStatus> = {
  [EQueryStatus.REJECTED]: {
    text: 'text-red-500',
    border: 'border-red-500',
    background: 'bg-red-100',
  },
  [EQueryStatus.NOT_VERIFIED]: {
    text: 'text-slate-500',
    border: 'border-slate-500',
    background: 'bg-slate-200',
  },
  [EQueryStatus.VERIFIED]: {
    text: 'text-green-700',
    border: 'border-green-700',
    background: 'bg-green-100',
  },
}

export const QUERY_STATUS_EXPLANATION: Record<QueryWorkspaceStatus, string> = {
  [EQueryStatus.REJECTED]: `The question is invalid, such as in the case of insufficient data or an unanswerable question`,
  [EQueryStatus.NOT_VERIFIED]:
    'The query is not used to improve the platform accuracy',
  [EQueryStatus.VERIFIED]:
    'The query is part of the Golden SQL training set to improve the platform accuracy',
}

export const DOMAIN_QUERY_STATUS_COLORS: ResourceColors<DomainQueryStatus> = {
  [EDomainQueryStatus.INITIALIZED]: {
    text: 'text-yellow-500',
  },
  [EDomainQueryStatus.REJECTED]: {
    text: 'text-red-500',
  },
  [EDomainQueryStatus.ERROR]: {
    text: 'text-red-500',
  },
  [EDomainQueryStatus.NOT_VERIFIED]: {
    text: 'text-slate-500',
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

export const getConfidence = (
  confidence_score: number,
): EDomainQueryConfidence => {
  if (confidence_score < 70) {
    return EDomainQueryConfidence.LOW_CONFIDENCE
  } else if (confidence_score < 90) {
    return EDomainQueryConfidence.MEDIUM_CONFIDENCE
  } else {
    return EDomainQueryConfidence.HIGH_CONFIDENCE
  }
}

export const getDomainStatus = (
  status: QueryStatus,
  confidence_score: number | null,
): DomainQueryStatus | undefined => {
  switch (status) {
    case EQueryStatus.INITIALIZED:
      return EDomainQueryStatus.INITIALIZED
    case EQueryStatus.REJECTED:
      return EDomainQueryStatus.REJECTED
    case EQueryStatus.ERROR:
      return EDomainQueryStatus.ERROR
    case EQueryStatus.NOT_VERIFIED: {
      if (confidence_score === null) {
        return status as DomainQueryStatus
      }
      return getConfidence(confidence_score)
    }
    case EQueryStatus.VERIFIED:
      return EDomainQueryStatus.VERIFIED
  }
}

export const getDomainStatusColors = (
  status: QueryStatus,
  confidence_score: number | null,
): ColorClasses => {
  const domainStatus = getDomainStatus(
    status,
    confidence_score,
  ) as DomainQueryStatus
  return DOMAIN_QUERY_STATUS_COLORS[domainStatus]
}

export const formatQueryStatus = (
  status?: DomainQueryStatus | QueryStatus,
): string => {
  if (status) {
    const formattedStatus = capitalize(status?.replace('_', ' ').toLowerCase())
    if (status === EQueryStatus.ERROR) {
      return formattedStatus.replace('Sql', 'SQL')
    }
    return formattedStatus
  }
  return ''
}

export const formatQueryStatusWithScore = (
  status: DomainQueryStatus | QueryStatus | undefined,
  confidence_score: number | null,
): string => {
  const formattedStatus = formatQueryStatus(status)
  if (
    status === EQueryStatus.ERROR ||
    confidence_score === null ||
    (status === EQueryStatus.NOT_VERIFIED && confidence_score === null)
  ) {
    return formattedStatus
  } else if (status === EQueryStatus.REJECTED) {
    return formattedStatus + ' by Admin'
  } else {
    const formattedScore =
      status === EQueryStatus.VERIFIED ? '(100%)' : `(${confidence_score}%)`
    return `${formattedStatus} ${formattedScore}`
  }
}

export const formatQueryConfidence = (confidence_score: number): string =>
  `${formatQueryStatus(getConfidence(confidence_score))} (${confidence_score}%)`

export const isVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.VERIFIED === status

export const isNotVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.NOT_VERIFIED === status

export const isRejected = (status?: QueryStatus): boolean =>
  EQueryStatus.REJECTED === status

export const isSqlError = (status?: QueryStatus): boolean =>
  EQueryStatus.ERROR === status
