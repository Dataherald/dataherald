import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { useSubscription } from '@/contexts/subscription-context'
import { isErrorResponse, isSubscriptionErrorCode } from '@/lib/domain/error'
import { ErrorResponse } from '@/models/api'
import { useRouter } from 'next/navigation'
import { useCallback, useState } from 'react'

interface ApiFetcherArgs {
  url: string
  options?: RequestInit
  retry?: boolean
  params?: URLSearchParams
}

interface ApiFetcher {
  apiFetcher: <T>(
    url: string,
    options?: RequestInit,
    retry?: boolean,
    params?: URLSearchParams,
  ) => Promise<T>
  apiFetcherV2: <T>(args: ApiFetcherArgs) => Promise<T>
  cancelApiFetch: () => void
  apiDownloadFile: (endpointUrl: string) => Promise<Blob | null>
}

const useApiFetcher = (): ApiFetcher => {
  const { token, fetchToken } = useAuth()
  const { setSubscriptionStatus } = useSubscription()
  const router = useRouter()

  const [controller, setController] = useState(new AbortController())

  /**
   * @deprecated Use apiFetcherV2 instead
   * TODO -- migrate SWR default fetcher to use apiFetcherV2
   */
  const apiFetcher = useCallback(
    async <T>(
      url: string,
      options?: RequestInit,
      retry = true,
      params?: URLSearchParams,
    ): Promise<T> => {
      if (!token) return Promise.resolve(null as unknown as T)
      const headers = {
        Authorization: `Bearer ${token}`,
        ...(!(options?.body instanceof FormData)
          ? { 'Content-Type': 'application/json' }
          : {}),
        ...(options?.headers || {}),
      }

      if (params) {
        url += `?${params.toString()}`
      }

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers,
      })

      if (!response.ok) {
        if (response.status === 401) {
          if (retry === false) {
            console.error(`Authentication failed. Redirecting to login page...`)
            router.push('api/auth/logout')
          }
          try {
            await fetchToken()
            return apiFetcher<T>(url, { ...options }, false)
          } catch (e) {
            console.error(
              `Authentication failed: ${e}. Redirecting to login page...`,
            )
            router.push('api/auth/logout')
          }
        } else {
          const errorResponse = await response.json()
          if (isErrorResponse(errorResponse)) {
            if (isSubscriptionErrorCode(errorResponse.error_code)) {
              setSubscriptionStatus(errorResponse.error_code)
            }

            throw errorResponse
          } else {
            const unhandledError: ErrorResponse = {
              error_code: 'UNHANDLED_ERROR',
              message: 'Unhandled server error',
              trace_id: '',
            }
            throw unhandledError
          }
        }
      }
      return response.json()
    },
    [controller.signal, fetchToken, router, setSubscriptionStatus, token],
  )

  /**
   * Wrapper of the `apiFetcher` but with a different signature
   * Object args signature is better for several optional parameters
   */
  const apiFetcherV2 = useCallback(
    async <T>({
      url,
      options,
      retry = true,
      params,
    }: {
      url: string
      options?: RequestInit
      retry?: boolean
      params?: URLSearchParams
    }): Promise<T> => apiFetcher(url, options, retry, params),
    [apiFetcher],
  )

  const cancelApiFetch = useCallback(() => {
    controller.abort()
    setController(new AbortController())
  }, [controller])

  const apiDownloadFile = async (endpointUrl: string): Promise<Blob | null> => {
    try {
      const response = await fetch(`${API_URL}/${endpointUrl}`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) {
        console.error('Download error:', response.statusText)
        throw new Error(response.statusText)
      }

      return await response.blob()
    } catch (error) {
      console.error('Download error:', error)
      throw error
    }
  }

  return { apiFetcher, apiFetcherV2, cancelApiFetch, apiDownloadFile }
}

export default useApiFetcher
