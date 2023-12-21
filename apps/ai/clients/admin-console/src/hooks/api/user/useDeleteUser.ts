import { API_URL } from '@/config'
import useDelete from '@/hooks/api/generics/useDelete'

export const useDeleteUser = () => {
  const deleteUser = useDelete()
  return (userId: string) => deleteUser(`${API_URL}/users/${userId}`)
}
