import usePagination, { PageResponse } from '@/hooks/api/generics/usePagination'
import { mapQuery } from '@/lib/domain/query'
import { QueryListItem } from '@/models/api'

const useQueries = (): PageResponse<QueryListItem> =>
  usePagination<QueryListItem>({
    resourceUrl: '/generations',
    itemMapper: mapQuery,
  })

export default useQueries
