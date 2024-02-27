import { API_URL } from '@/config'
import { useAppContext } from '@/contexts/app-context'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, SpendingLimits } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface SpendingLimitsResponse {
  limits: SpendingLimits | undefined
  isLoading: boolean
  isValidating: boolean
  error: ErrorResponse | null
  mutate: KeyedMutator<SpendingLimits>
}

const useSpendingLimits = (): SpendingLimitsResponse => {
  const { token } = useAuth()
  const { organization } = useAppContext()
  const endpointUrl = `${API_URL}/organizations/${organization?.id}/invoices/limits`
  const { data, isLoading, isValidating, error, mutate } =
    useSWR<SpendingLimits>(token && organization ? endpointUrl : null)
  return {
    limits: data,
    isLoading: isLoading || (!data && !error),
    isValidating,
    error,
    mutate,
  }
}

export default useSpendingLimits
