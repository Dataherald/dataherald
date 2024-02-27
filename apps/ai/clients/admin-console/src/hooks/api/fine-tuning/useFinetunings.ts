import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, FineTuningModels } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface FineTuningModelsResponse {
  models: FineTuningModels | undefined
  isLoading: boolean
  isValidating: boolean
  error: ErrorResponse | null
  mutate: KeyedMutator<FineTuningModels>
}

const useFinetunings = (): FineTuningModelsResponse => {
  const endpointUrl = `${API_URL}/finetunings`
  const { token } = useAuth()
  const { data, isLoading, isValidating, error, mutate } =
    useSWR<FineTuningModels>(token ? endpointUrl : null)
  return {
    models: data,
    isLoading: isLoading || (!data && !error),
    isValidating,
    error,
    mutate,
  }
}

export default useFinetunings
