import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { FineTuningModels } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface FineTuningModelsResponse {
  models: FineTuningModels | undefined
  isLoading: boolean
  error: unknown
  mutate: KeyedMutator<FineTuningModels>
}

const useFinetunings = (): FineTuningModelsResponse => {
  const endpointUrl = `${API_URL}/finetunings`
  const { token } = useAuth()
  const { data, isLoading, error, mutate } = useSWR<FineTuningModels>(
    token ? endpointUrl : null,
  )
  return {
    models: data,
    isLoading: isLoading || (!data && !error),
    error,
    mutate,
  }
}

export default useFinetunings
