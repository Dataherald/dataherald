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

export const formatQueryStatus = (status?: DomainQueryStatus) =>
  status?.replace('_', ' ').toLowerCase()
