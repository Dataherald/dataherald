import usePagination, { PageResponse } from '@/hooks/api/usePagination'
import { QueryListItem } from '@/models/api'

const useQueries = (): PageResponse<QueryListItem> =>
  usePagination<QueryListItem>('/query/list')

export default useQueries
