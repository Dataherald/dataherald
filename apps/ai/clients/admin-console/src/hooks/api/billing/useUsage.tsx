import { API_URL } from '@/config'
import { useAppContext } from '@/contexts/app-context'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, Usage } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface UsageResponse {
  usage: Usage | undefined
  isLoading: boolean
  isValidating: boolean
  error: ErrorResponse | null
  mutate: KeyedMutator<Usage>
}

const useUsage = (): UsageResponse => {
  const { token } = useAuth()
  const { organization } = useAppContext()
  const endpointUrl = `${API_URL}/organizations/${organization?.id}/invoices/pending`
  const { data, isLoading, isValidating, error, mutate } = useSWR<Usage>(
    token && organization ? endpointUrl : null,
    { refreshInterval: 10000, errorRetryCount: 3 },
  )
  return {
    usage: data,
    isLoading: isLoading || (!data && !error),
    isValidating,
    error,
    mutate,
  }
}

export default useUsage
