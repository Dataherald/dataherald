import { API_URL } from '@/config'
import usePatch from '@/hooks/api/generics/usePatch'
import { User } from '@/models/api'

export const usePatchUser = () => {
  const patchUser = usePatch<User>()
  return (userId: string, changes: Partial<User>) =>
    patchUser(`${API_URL}/user/${userId}`, changes)
}
