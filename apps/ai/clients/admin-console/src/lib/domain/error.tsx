import { ErrorResponse } from '@/models/api'
import { ESubscriptionErrorCode } from '@/models/errorCodes'

export const isErrorResponse = (error: unknown): error is ErrorResponse => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'error_code' in error
  )
}

export const isSubscriptionErrorCode = (
  errorCode: string,
): errorCode is ESubscriptionErrorCode => {
  return Object.values(ESubscriptionErrorCode).includes(
    errorCode as ESubscriptionErrorCode,
  )
}
