import usePagination, { PageResponse } from '@/hooks/api/generics/usePagination'
import { GoldenSqlListItem } from '@/models/api'

const useGoldenSqlList = (): PageResponse<GoldenSqlListItem> =>
  usePagination<GoldenSqlListItem>('/golden-sqls')

export default useGoldenSqlList
