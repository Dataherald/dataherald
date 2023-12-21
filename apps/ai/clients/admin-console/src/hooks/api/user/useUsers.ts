import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { Users } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface UsersResponse {
  users: Users | undefined
  isLoading: boolean
  error: unknown
  mutate: KeyedMutator<Users>
}

const useUsers = (): UsersResponse => {
  const endpointUrl = `${API_URL}/users`
  const { token } = useAuth()
  const { data, isLoading, error, mutate } = useSWR<Users>(
    token ? endpointUrl : null,
  )

  return {
    users: data,
    isLoading: isLoading || (!data && !error),
    error,
    mutate,
  }
}

export default useUsers
