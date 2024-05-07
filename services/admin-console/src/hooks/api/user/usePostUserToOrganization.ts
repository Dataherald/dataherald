import { API_URL } from '@/config'
import usePost from '@/hooks/api/generics/usePost'

type PostUserToOrganizationRequest = { email: string }

export const usePostUserToOrganization = () => {
  const postUserToOrganization = usePost<PostUserToOrganizationRequest, void>()
  return (resource: PostUserToOrganizationRequest) =>
    postUserToOrganization(`${API_URL}/users/invite`, resource)
}
