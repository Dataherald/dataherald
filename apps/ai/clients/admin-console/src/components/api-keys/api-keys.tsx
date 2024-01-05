import { apiKeysColumns } from '@/components/api-keys/columns'
import ApiKeysError from '@/components/api-keys/error'
import GenerateApiKeyDialog from '@/components/api-keys/generate-api-key-dialog'
import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import { Button } from '@/components/ui/button'
import useApiKeys from '@/hooks/api/api-keys/useApiKeys'
import { KeyRound, Plus } from 'lucide-react'
import { useMemo, useState } from 'react'

const ApiKeys = () => {
  const [openGenerateKeyDialog, setOpenGenerateKeyDialog] = useState(false)
  const { isLoading, error, apiKeys, mutate } = useApiKeys()
  const columns = useMemo(() => apiKeysColumns, [])

  const handleClose = async () => {
    setOpenGenerateKeyDialog(false)
  }

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
        <Button onClick={() => setOpenGenerateKeyDialog(true)}>
          <Plus className="mr-2" />
          Generate new secret key
        </Button>
        <GenerateApiKeyDialog
          open={openGenerateKeyDialog}
          onGeneratedKey={() => mutate()}
          onClose={handleClose}
        />
      </div>
    </>
  )
}

export default ApiKeys
