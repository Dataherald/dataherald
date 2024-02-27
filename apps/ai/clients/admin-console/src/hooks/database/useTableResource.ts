import { TreeNode } from '@/components/ui/tree-view'
import { toast } from '@/components/ui/use-toast'
import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { UseDatabaseResourceFromTree } from '@/hooks/database/useDatabaseResourceFromTree'
import { isTableResource } from '@/lib/domain/database'
import { ErrorResponse, TableDescription } from '@/models/api'
import { DatabaseResourceType, TableResource } from '@/models/domain'
import { useCallback } from 'react'
import useSWR, { mutate } from 'swr'

export const useTableResource = (
  node: TreeNode | null,
): UseDatabaseResourceFromTree<TableResource> => {
  const TABLE_DESCRIPTION_ENDPOINT_URL = `${API_URL}/table-descriptions`
  const { apiFetcher } = useApiFetcher()

  const isNodeTableResource = node && isTableResource(node.type)

  const resourceUrl = isNodeTableResource
    ? `${TABLE_DESCRIPTION_ENDPOINT_URL}/${node.id}`
    : null

  const {
    data: tableDescription,
    isLoading,
    error,
  } = useSWR<TableDescription>(resourceUrl, apiFetcher, {
    revalidateOnFocus: false,
    revalidateIfStale: false,
  })

  const resource: TableResource | null = isNodeTableResource
    ? {
        id: node.id,
        type: node.type as DatabaseResourceType,
        icon: node.icon,
        name: node.name,
        description: tableDescription?.description || '',
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
            body: JSON.stringify({ description: newDescription }),
          }),
        )
        toast({
          variant: 'success',
          title: `${tableDescription?.table_name} description updated`,
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
      resourceUrl,
      tableDescription?.id,
      tableDescription?.table_name,
    ],
  )

  return { resource, isLoading, error, updateResource }
}
