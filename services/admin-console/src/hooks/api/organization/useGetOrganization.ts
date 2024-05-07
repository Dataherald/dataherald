import { API_URL } from '@/config'
import useGet from '@/hooks/api/generics/useGet'
import { Organization } from '@/models/api'

export const useGetOrganization = () => {
  const getOrganization = useGet<Organization>()
  return (organizationId: string) =>
    getOrganization(`${API_URL}/organizations/${organizationId}`)
}
