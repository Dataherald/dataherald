import { API_URL } from '@/config'
import usePut from '@/hooks/api/generics/usePut'
import { Organization } from '@/models/api'

export const usePutOrganization = () => {
  const putOrganization = usePut<Organization>()
  return (organizationId: string, newOrganization: Organization) =>
    putOrganization(
      `${API_URL}/organizations/${organizationId}`,
      newOrganization,
    )
}
