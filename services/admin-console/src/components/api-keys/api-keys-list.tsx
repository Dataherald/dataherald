import { getApiKeysColumns } from '@/components/api-keys/columns'
import GenerateApiKeyDialog from '@/components/api-keys/generate-api-key-dialog'
import { DataTable } from '@/components/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import PageErrorMessage from '@/components/error/page-error-message'
import { Button } from '@/components/ui/button'
import useApiKeys from '@/hooks/api/api-keys/useApiKeys'
import { useDeleteApiKey } from '@/hooks/api/api-keys/useDeleteApiKey'
import { KeyRound, RefreshCcw } from 'lucide-react'
import { useCallback, useMemo } from 'react'

const ApiKeysList = () => {
  const { isLoading, isValidating, error, apiKeys, mutate } = useApiKeys()
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

  const handleRefresh = useCallback(async () => {
    mutate()
  }, [mutate])

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
    pageContent = (
      <PageErrorMessage
        message="Something went wrong while fetching your API keys. Please try
        again later."
        error={error}
      />
    )
  } else if (apiKeys?.length === 0) {
    pageContent = (
      <div className="text-slate-500">No API keys generated yet.</div>
    )
  } else {
    pageContent = apiKeys ? (
      <DataTable id="api-keys" columns={columns} data={apiKeys} />
    ) : (
      <></>
    )
  }

  return (
    <>
      <div className="w-full flex justify-between gap-2">
        <div className="flex items-center gap-2">
          <KeyRound size={20} strokeWidth={2.5} />
          <h1 className="font-semibold">API Keys</h1>
        </div>
        <Button
          variant="ghost"
          size="icon"
          disabled={isLoading || isValidating}
          onClick={handleRefresh}
        >
          <RefreshCcw
            size={16}
            className={isLoading || isValidating ? 'animate-spin' : ''}
          />
        </Button>
      </div>
      <div className="grow">{pageContent}</div>
      <div className="self-end">
        <GenerateApiKeyDialog onGeneratedKey={handleRefresh} />
      </div>
    </>
  )
}

export default ApiKeysList
