import { TreeNode } from '@/components/ui/tree-view'
import { toast } from '@/components/ui/use-toast'
import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { UseDatabaseResourceFromTree } from '@/hooks/database/useDatabaseResourceFromTree'
import { isDatabaseResource } from '@/lib/domain/database'
import { ErrorResponse, Instruction } from '@/models/api'
import { DatabaseResource, DatabaseResourceType } from '@/models/domain'
import { useCallback } from 'react'
import useSWR, { mutate } from 'swr'

export const useDatabaseResource = (
  node: TreeNode | null,
): UseDatabaseResourceFromTree<DatabaseResource> => {
  const INSTRUCTION_URL = `${API_URL}/instructions`
  const { apiFetcher } = useApiFetcher()

  const isNodeDatabaseResource = node && isDatabaseResource(node.type)

  const resourceUrl = isNodeDatabaseResource
    ? `${INSTRUCTION_URL}/first?db_connection_id=${node.id}`
    : null

  const {
    data: databaseInstruction,
    isLoading,
    error,
  } = useSWR<Instruction>(resourceUrl, apiFetcher, {
    revalidateOnFocus: false,
    revalidateIfStale: false,
  })

  const resource: DatabaseResource | null = isNodeDatabaseResource
    ? {
        id: node.id,
        type: node.type as DatabaseResourceType,
        icon: node.icon,
        name: node.name,
        instructions: databaseInstruction?.instruction || '',
      }
    : null

  const updateResource = useCallback(
    async (newInstruction: string) => {
      const method = databaseInstruction ? 'PUT' : 'POST'
      const url = databaseInstruction
        ? `${INSTRUCTION_URL}/${databaseInstruction.id}` // PUT
        : `${INSTRUCTION_URL}` // POST

      try {
        await mutate(
          resourceUrl,
          apiFetcher(url, {
            method,
            body: JSON.stringify({
              instruction: newInstruction,
              db_connection_id: node?.id,
            }),
          }),
        )
        toast({ variant: 'success', title: 'Database instructions updated' })
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
    [INSTRUCTION_URL, apiFetcher, databaseInstruction, node?.id, resourceUrl],
  )

  return { resource, isLoading, error, updateResource }
}
