import { EQueryStatus, QueryEvaluation, QueryStatus } from '@/models/api'
import {
  DomainQueryStatus,
  EDomainQueryStatus,
  EDomainQueryStatusTextColor,
} from '@/models/domain'

export const getDomainStatus = (
  status: QueryStatus,
  evaluation: QueryEvaluation,
): DomainQueryStatus | undefined => {
  const { confidence_level } = evaluation
  switch (status) {
    case EQueryStatus.SQL_ERROR:
      return EDomainQueryStatus.SQL_ERROR
    case EQueryStatus.NOT_VERIFIED: {
      if (confidence_level < 70) {
        return EDomainQueryStatus.LOW_CONFIDENCE
      } else if (confidence_level < 90) {
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
  evaluation: QueryEvaluation,
): EDomainQueryStatusTextColor => {
  const domainStatus = getDomainStatus(status, evaluation) as DomainQueryStatus
  return EDomainQueryStatusTextColor[domainStatus]
}

export const formatQueryStatus = (status?: DomainQueryStatus) =>
  status?.replace('_', ' ').toLowerCase()
