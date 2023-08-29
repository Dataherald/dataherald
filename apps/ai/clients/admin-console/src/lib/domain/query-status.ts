import { EQueryStatus, QueryStatus } from '@/models/api'
import {
  DomainQueryStatus,
  EDomainQueryStatus,
  EDomainQueryStatusTextColor,
} from '@/models/domain'

export const getDomainStatus = (
  status: QueryStatus,
  evaluation_score: number,
): DomainQueryStatus | undefined => {
  switch (status) {
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

export const getDomainStatusColor = (
  status: QueryStatus,
  evaluation_score: number,
): EDomainQueryStatusTextColor => {
  const domainStatus = getDomainStatus(
    status,
    evaluation_score,
  ) as DomainQueryStatus
  return EDomainQueryStatusTextColor[domainStatus]
}

export const formatQueryStatus = (
  status?: DomainQueryStatus | QueryStatus,
): string => {
  if (status) {
    const formattedStatus = status?.replace('_', ' ').toLowerCase()
    return status === EQueryStatus.SQL_ERROR
      ? formattedStatus.replace('sql', 'SQL')
      : formattedStatus
  }
  return ''
}

export const formatQueryStatusWithScore = (
  status: DomainQueryStatus | QueryStatus | undefined,
  evaluation_score: number,
): string => {
  const formattedStatus = formatQueryStatus(status)
  const formattedScore =
    status === EQueryStatus.VERIFIED
      ? '(100%)'
      : status === EQueryStatus.SQL_ERROR
      ? ''
      : `(${evaluation_score}%)`
  return `${formattedStatus} ${formattedScore}`
}

export const isVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.VERIFIED === status

export const isNotVerified = (status?: QueryStatus): boolean =>
  EQueryStatus.NOT_VERIFIED === status
