import { API_URL } from '@/config'
import { useAuth } from '@/contexts/auth-context'
import { apiFetcher } from '@/lib/api/fetcher'
import { GoldenSqlList } from '@/models/api'
import { KeyedMutator } from 'swr'

export const useDeleteGoldenSql = (
  listMutator: KeyedMutator<GoldenSqlList[]>,
) => {
  const { token } = useAuth()

  const deleteGoldenSqlQuery = async (id: string) => {
    try {
      await apiFetcher(`${API_URL}/golden-sql/${id}`, {
        method: 'DELETE',
        token: token as string,
      })

      listMutator((list) => {
        return list?.map((page) => page?.filter((item) => item.id !== id))
      }, true)
    } catch (error) {
      console.error('Error deleting item:', error)
      throw error
    }
  }

  return deleteGoldenSqlQuery
}
