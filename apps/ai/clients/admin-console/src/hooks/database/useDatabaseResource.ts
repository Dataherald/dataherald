import { TreeNode } from '@/components/ui/tree-view'
import { toast } from '@/components/ui/use-toast'
import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { UseDatabaseResourceFromTree } from '@/hooks/database/useDatabaseResourceFromTree'
import { isDatabaseResource } from '@/lib/domain/database'
import { Instruction } from '@/models/api'
import { DatabaseResource, DatabaseResourceType } from '@/models/domain'
import { useCallback } from 'react'
import useSWR, { mutate } from 'swr'

export const useDatabaseResource = (
  node: TreeNode | null,
): UseDatabaseResourceFromTree<DatabaseResource> => {
  const INSTRUCTION_URL = `${API_URL}/instruction`
  const apiFetcher = useApiFetcher()

  const isNodeDatabaseResource = node && isDatabaseResource(node.type)

  const resourceUrl = isNodeDatabaseResource ? INSTRUCTION_URL : null

  const {
    data: databaseInstruction,
    isLoading,
    error,
  } = useSWR<Instruction>(resourceUrl, apiFetcher, {
    errorRetryCount: 0,
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
            body: JSON.stringify({ instruction: newInstruction }),
          }),
        )
        toast({ variant: 'success', title: 'Database instructions updated' })
      } catch (e) {
        toast({
          variant: 'destructive',
          title: 'Oops! Something went wrong',
          description: 'Database instructions could not be updated',
        })
      }
    },
    [INSTRUCTION_URL, apiFetcher, databaseInstruction, resourceUrl],
  )

  return { resource, isLoading, error, updateResource }
}
