import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { GoldenSqlList } from '@/models/api'
import { KeyedMutator } from 'swr'

export const useDeleteGoldenSql = (
  listMutator: KeyedMutator<GoldenSqlList[]>,
) => {
  const { apiFetcher } = useApiFetcher()
  const deleteGoldenSqlQuery = async (id: string) => {
    try {
      await apiFetcher(`${API_URL}/golden-sqls/${id}`, {
        method: 'DELETE',
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
