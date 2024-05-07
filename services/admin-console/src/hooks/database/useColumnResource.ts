import { TreeNode } from '@/components/ui/tree-view'
import { toast } from '@/components/ui/use-toast'
import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { UseDatabaseResourceFromTree } from '@/hooks/database/useDatabaseResourceFromTree'
import { isColumnResource } from '@/lib/domain/database'
import {
  ColumnDescription,
  ErrorResponse,
  TableDescription,
} from '@/models/api'
import { ColumnResource, DatabaseResourceType } from '@/models/domain'
import { useCallback } from 'react'
import useSWR, { mutate } from 'swr'

export const useColumnResource = (
  node: TreeNode | null,
): UseDatabaseResourceFromTree<ColumnResource> => {
  const TABLE_DESCRIPTION_ENDPOINT_URL = `${API_URL}/table-descriptions`
  const { apiFetcher } = useApiFetcher()

  const isNodeColumnResource = node && isColumnResource(node.type)

  const resourceUrl = isNodeColumnResource
    ? `${TABLE_DESCRIPTION_ENDPOINT_URL}/${node.id}` // the node id is the table id for columns as it is not a resource itself
    : null

  const {
    data: tableDescription,
    isLoading,
    error,
  } = useSWR<TableDescription>(resourceUrl, apiFetcher, {
    revalidateOnFocus: false,
    revalidateIfStale: false,
  })

  const columnDescription: ColumnDescription | undefined =
    tableDescription?.columns.find((c) => c.name === node?.name)

  const resource: ColumnResource | null = isNodeColumnResource
    ? {
        id: node.id,
        type: node.type as DatabaseResourceType,
        icon: node.icon,
        name: node.name,
        description: columnDescription?.description || '',
        categories: columnDescription?.categories,
      }
    : null

  const updateResource = useCallback(
    async (newDescription: string) => {
      const url = `${TABLE_DESCRIPTION_ENDPOINT_URL}/${tableDescription?.id}`
      try {
        await mutate(
          resourceUrl,
          apiFetcher(url, {
            method: 'PUT',
            body: JSON.stringify({
              columns: [{ ...columnDescription, description: newDescription }],
            }),
          }),
        )
        toast({
          variant: 'success',
          title: `${columnDescription?.name} description updated`,
        })
      } catch (e) {
        console.error(e)
        const { message: title, trace_id: description } = e as ErrorResponse
        toast({
          variant: 'destructive',
          title,
          description,
        })
      }
    },
    [
      TABLE_DESCRIPTION_ENDPOINT_URL,
      apiFetcher,
      columnDescription,
      resourceUrl,
      tableDescription?.id,
    ],
  )

  return { resource, isLoading, error, updateResource }
}
