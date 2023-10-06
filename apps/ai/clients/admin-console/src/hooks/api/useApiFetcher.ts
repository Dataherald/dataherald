import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { useCallback } from 'react'

const useApiFetcher = () => {
  const { token, fetchToken } = useAuth()
  const router = useRouter()

  const apiFetcher = useCallback(
    async <T>(url: string, options?: RequestInit, retry = true): Promise<T> => {
      const headers = {
        Authorization: `Bearer ${token}`,
        ...(!(options?.body instanceof FormData)
          ? { 'Content-Type': 'application/json' }
          : {}),
        ...(options?.headers || {}),
      }

      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        if (response.status === 401 && retry) {
          try {
            await fetchToken()
            return apiFetcher<T>(url, { ...options }, false)
          } catch (e) {
            console.error(
              `Authentication failed: ${e}. Redirecting to login page...`,
            )
            router.push('api/auth/login')
          }
        } else {
          const error = new Error(
            `API Request failed\nURL: ${url}\nStatus: ${response.status} ${response.statusText}`,
            { cause: response.status },
          )
          throw error
        }
      }

      return response.json()
    },
    [token, fetchToken, router],
  )

  return apiFetcher
}

export default useApiFetcher
