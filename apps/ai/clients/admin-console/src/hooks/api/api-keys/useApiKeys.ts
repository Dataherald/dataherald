import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { ApiKeys } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface ApiKeysResponse {
  apiKeys: ApiKeys | undefined
  isLoading: boolean
  error: unknown
  mutate: KeyedMutator<ApiKeys>
}

const useApiKeys = (): ApiKeysResponse => {
  const endpointUrl = `${API_URL}/keys`
  const { token } = useAuth()
  const { data, isLoading, error, mutate } = useSWR<ApiKeys>(
    token ? endpointUrl : null,
  )
  return {
    apiKeys: data,
    isLoading: isLoading || (!data && !error),
    error,
    mutate,
  }
}

export default useApiKeys
