import { API_URL } from '@/config'
import { apiFetcher } from '@/lib/api/fetcher'
import { Query } from '@/models/api'

export const executeQuery = async (
  queryId: string,
  sql_query: string,
): Promise<Query> =>
  apiFetcher<Query>(`${API_URL}/query/${queryId}/execution`, {
    method: 'POST',
    body: JSON.stringify({ sql_query }),
  })
