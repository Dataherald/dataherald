import { API_URL } from '@/config'
import usePut from '@/hooks/api/generics/usePut'
import { User } from '@/models/api'

export const usePutUser = () => {
  const putUser = usePut<User>()
  return (userId: string, changes: User) =>
    putUser(`${API_URL}/users/${userId}`, changes)
}
