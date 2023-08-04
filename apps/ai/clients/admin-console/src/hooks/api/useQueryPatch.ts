import { API_URL } from '@/config'
import { apiFetcher } from '@/lib/api/fetcher'
import { Query, QueryStatus } from '@/models/api'

export const patchQuery = async (
  queryId: string,
  patches: {
    sql_query: string
    query_status: QueryStatus
  },
): Promise<Query> =>
  apiFetcher<Query>(`${API_URL}/query/${queryId}/`, {
    method: 'PATCH',
    body: JSON.stringify(patches),
  })
