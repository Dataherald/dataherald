import { getApiKeysColumns } from '@/components/api-keys/columns'
import ApiKeysError from '@/components/api-keys/error'
import GenerateApiKeyDialog from '@/components/api-keys/generate-api-key-dialog'
import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import useApiKeys from '@/hooks/api/api-keys/useApiKeys'
import { useDeleteApiKey } from '@/hooks/api/api-keys/useDeleteApiKey'
import { KeyRound } from 'lucide-react'
import { useCallback, useMemo } from 'react'

const ApiKeys = () => {
  const { isLoading, error, apiKeys, mutate } = useApiKeys()
  const deleteApiKey = useDeleteApiKey<void>()

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteApiKey(id)
        mutate() // update the list of api keys
        return Promise.resolve()
      } catch (e) {
        return Promise.reject(e)
      }
    },
    [deleteApiKey, mutate],
  )

  const columns = useMemo(
    () => getApiKeysColumns({ remove: handleDelete }),
    [handleDelete],
  )

  let pageContent = <></>

  if (isLoading) {
    pageContent = (
      <LoadingTable columnLength={4} rowLength={4} className="rounded-none" />
    )
  } else if (error) {
    pageContent = <ApiKeysError />
  } else if (apiKeys?.length === 0) {
    pageContent = (
      <div className="text-slate-500">No API keys generated yet.</div>
    )
  } else {
    pageContent = apiKeys ? (
      <DataTable columns={columns} data={apiKeys} />
    ) : (
      <></>
    )
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <KeyRound size={20} strokeWidth={2.5} />
        <h1 className="font-semibold">API Keys</h1>
      </div>
      <div className="grow overflow-auto">{pageContent}</div>
      <div className="self-end">
        <GenerateApiKeyDialog onGeneratedKey={() => mutate()} />
      </div>
    </>
  )
}

export default ApiKeys
