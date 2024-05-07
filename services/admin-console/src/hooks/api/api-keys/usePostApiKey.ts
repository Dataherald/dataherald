import { API_URL } from '@/config'
import usePost from '@/hooks/api/generics/usePost'
import { ApiKey } from '@/models/api'

type PostApiKeyRequest = { name: string }

export const usePostApiKey = () => {
  const postApiKey = usePost<PostApiKeyRequest, ApiKey>()
  return (resource: PostApiKeyRequest) =>
    postApiKey(`${API_URL}/keys`, resource)
}
