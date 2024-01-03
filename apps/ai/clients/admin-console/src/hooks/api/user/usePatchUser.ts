import { API_URL } from '@/config'
import usePatch from '@/hooks/api/generics/usePatch'
import { User } from '@/models/api'

export const usePatchUser = () => {
  const patchUser = usePatch<User>()
  return (userId: string, changes: User) =>
    patchUser(`${API_URL}/users/${userId}`, changes)
}
