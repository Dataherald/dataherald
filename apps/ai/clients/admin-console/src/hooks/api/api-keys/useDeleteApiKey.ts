import { API_URL } from '@/config'
import useDelete from '@/hooks/api/generics/useDelete'

export const useDeleteApiKey = <T = void>() => {
  const deleteApiKey = useDelete<T>()
  return (apiKeyId: string) => deleteApiKey(`${API_URL}/keys/${apiKeyId}`)
}
