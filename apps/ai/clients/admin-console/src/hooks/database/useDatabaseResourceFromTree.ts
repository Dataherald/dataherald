import { useTree } from '@/components/ui/tree-view-context'
import {
  isColumnResource,
  isDatabaseResource,
  isTableResource,
} from '@/lib/domain/database'
import {
  ColumnResource,
  DatabaseResource,
  DatabaseResourceType,
  TableResource,
} from '@/models/domain'
import { useColumnResource } from './useColumnResource'
import { useDatabaseResource } from './useDatabaseResource'
import { useTableResource } from './useTableResource'

export interface UseDatabaseResourceFromTree<R> {
  resource: R | null
  isLoading: boolean
  error: unknown
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
