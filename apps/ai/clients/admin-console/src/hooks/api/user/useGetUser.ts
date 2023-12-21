import { API_URL } from '@/config'
import useGet from '@/hooks/api/generics/useGet'
import { User } from '@/models/api'

export const useGetUser = () => {
  const getUser = useGet<User>()
  return (userId: string) => getUser(`${API_URL}/users/${userId}`)
}
