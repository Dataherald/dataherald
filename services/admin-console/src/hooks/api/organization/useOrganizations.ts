import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, Organizations } from '@/models/api'
import useSWR from 'swr'

interface OrganizationsResponse {
  organizations: Organizations | undefined
  isLoading: boolean
  error: ErrorResponse | null
}

const useOrganizations = (): OrganizationsResponse => {
  const endpointUrl = `${API_URL}/organizations`
  const { token } = useAuth()
  const { data, isLoading, error } = useSWR<Organizations>(
    token ? endpointUrl : null,
  )

  return {
    organizations: data,
    isLoading: isLoading || (!data && !error),
    error,
  }
}

export default useOrganizations
