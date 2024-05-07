import { useTree } from '@/components/ui/tree-view-context'
import { useColumnResource } from '@/hooks/database/useColumnResource'
import { useDatabaseResource } from '@/hooks/database/useDatabaseResource'
import { useTableResource } from '@/hooks/database/useTableResource'
import {
  isColumnResource,
  isDatabaseResource,
  isTableResource,
} from '@/lib/domain/database'
import { ErrorResponse } from '@/models/api'
import {
  ColumnResource,
  DatabaseResource,
  DatabaseResourceType,
  TableResource,
} from '@/models/domain'

export interface UseDatabaseResourceFromTree<R> {
  resource: R | null
  isLoading: boolean
  error: ErrorResponse | null
  updateResource: ((newText: string) => Promise<void>) | null
}

const useDatabaseResourceFromTree = (): UseDatabaseResourceFromTree<
  DatabaseResource | TableResource | ColumnResource
> => {
  const { clickedRow: clickedNode } = useTree()

  const databaseResource: UseDatabaseResourceFromTree<DatabaseResource> =
    useDatabaseResource(clickedNode)
  const tableResource: UseDatabaseResourceFromTree<TableResource> =
    useTableResource(clickedNode)
  const columnResource: UseDatabaseResourceFromTree<ColumnResource> =
    useColumnResource(clickedNode)

  if (isDatabaseResource(clickedNode?.type as DatabaseResourceType)) {
    return databaseResource
  }
  if (isTableResource(clickedNode?.type as DatabaseResourceType)) {
    return tableResource
  }
  if (isColumnResource(clickedNode?.type as DatabaseResourceType)) {
    return columnResource
  }
  return {
    resource: null,
    isLoading: false,
    error: null,
    updateResource: null,
  }
}

export default useDatabaseResourceFromTree
