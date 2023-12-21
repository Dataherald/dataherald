import { API_URL } from '@/config'
import usePost from '@/hooks/api/generics/usePost'

type PostUserRequest = { email: string }

export const usePostUser = () => {
  const postUser = usePost<PostUserRequest>()
  return (resource: PostUserRequest) => postUser(`${API_URL}/users`, resource)
}
