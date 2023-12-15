import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { useCallback } from 'react'

const useApiFetcher = () => {
  const { token, fetchToken } = useAuth()
  const router = useRouter()

  const apiFetcher = useCallback(
    async <T>(url: string, options?: RequestInit, retry = true): Promise<T> => {
      if (!token) return Promise.resolve(null as unknown as T)
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

  return { apiFetcher, apiDownloadFile }
}

export default useApiFetcher
