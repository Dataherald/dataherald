import { useTree } from '@/components/ui/tree-view-context'
import { toast } from '@/components/ui/use-toast'
import { API_URL } from '@/config'
import useApiFetcher from '@/hooks/api/useApiFetcher'
import { isDatabaseResource, isTableResource } from '@/lib/domain/database'
import { Instruction, TableDescription } from '@/models/api'
import { DatabaseResource, DatabaseResourceType } from '@/models/domain'
import { useCallback } from 'react'
import useSWR, { mutate } from 'swr'

const DATABASE_INSTRUCTION_ENDPOINT_URL = `${API_URL}/instruction`
const TABLE_DESCRIPTION_ENDPOINT_URL = `${API_URL}/table-description`

const MESSAGES: {
  [key in DatabaseResourceType]: { success: string; error: string }
} = {
  database: {
    success: 'Database instruction updated',
    error: 'There was a problem updating the database instructions',
  },
  table: {
    success: 'Table description updated',
    error: 'There was a problem updating the table description',
  },
  column: {
    success: 'Column description updated',
    error: 'There was a problem updating the column description',
  },
}

const useDatabaseResourceFromTree = (): {
  resource?: DatabaseResource
  isLoading: boolean
  error: unknown
  updateResource: (newText: string) => Promise<void>
} => {
  const { clickedRow: node } = useTree()
  const apiFetcher = useApiFetcher()

  const resourceType = node?.type as DatabaseResourceType

  let resourceUrl: string | null
  let resource: DatabaseResource | undefined
  if (node) {
    resourceUrl = isDatabaseResource(resourceType)
      ? `${DATABASE_INSTRUCTION_ENDPOINT_URL}`
      : `${TABLE_DESCRIPTION_ENDPOINT_URL}/${node?.id}`
  } else {
    resourceUrl = null // value for SWR to not fetch
    resource = undefined
  }

  const { data, isLoading, error } = useSWR<TableDescription | Instruction>(
    resourceUrl,
    apiFetcher,
    {
      errorRetryCount: isDatabaseResource(resourceType) ? 0 : 1,
      revalidateOnFocus: false,
      revalidateIfStale: false,
    },
  )

  let databaseInstruction: Instruction | undefined
  let tableDescription: TableDescription | undefined

  if (node) {
    if (isDatabaseResource(resourceType)) {
      databaseInstruction = data as Instruction
      resource = {
        id: node.id,
        type: node.type as DatabaseResourceType,
        icon: node.icon,
        name: node.name,
        text: databaseInstruction?.instruction || '',
      }
    } else {
      tableDescription = data as TableDescription
      if (isTableResource(resourceType)) {
        resource = {
          id: node.id,
          type: node.type as DatabaseResourceType,
          icon: node.icon,
          name: node.name,
          text: tableDescription?.description || '',
        }
      } else {
        //column type
        resource = {
          id: node.id,
          type: node.type as DatabaseResourceType,
          icon: node.icon,
          name: node.name,
          text:
            tableDescription?.columns?.find((c) => c.name === node?.name)
              ?.description || '',
        }
      }
    }
  }

  const getPayload = useCallback(
    (resourceText: string) => {
      if (isDatabaseResource(resourceType)) {
        return {
          instruction: resourceText,
        }
      } else {
        if (isTableResource(resourceType)) {
          return {
            description: resourceText,
          }
        } else {
          // column type
          return {
            columns: [
              {
                ...tableDescription?.columns?.find(
                  (c) => c.name === node?.name,
                ),
                description: resourceText,
              },
            ],
          }
        }
      }
    },
    [node?.name, resourceType, tableDescription?.columns],
  )

  const updateResource = useCallback(
    async (newText: string) => {
      const payload = getPayload(newText || '')
      const method = isDatabaseResource(resourceType)
        ? databaseInstruction
          ? 'PUT'
          : 'POST'
        : 'PATCH'
      const url = isDatabaseResource(resourceType)
        ? databaseInstruction
          ? `${DATABASE_INSTRUCTION_ENDPOINT_URL}/${databaseInstruction.id}` // PUT
          : `${DATABASE_INSTRUCTION_ENDPOINT_URL}` // POST
        : `${TABLE_DESCRIPTION_ENDPOINT_URL}/${tableDescription?.id}` // PATCH

      try {
        await mutate(
          resourceUrl,
          apiFetcher(url, {
            method,
            body: JSON.stringify(payload),
          }),
        )
        toast({ variant: 'success', title: MESSAGES[resourceType].success })
      } catch (e) {
        toast({
          variant: 'destructive',
          title: 'Ups! Something went wrong',
          description: MESSAGES[resourceType].error,
        })
      }
    },
    [
      getPayload,
      resourceType,
      databaseInstruction,
      tableDescription?.id,
      resourceUrl,
      apiFetcher,
    ],
  )

  return {
    resource,
    isLoading,
    error,
    updateResource,
  }
}

export default useDatabaseResourceFromTree
