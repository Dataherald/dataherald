import { apiKeysColumns } from '@/components/api-keys/columns'
import ApiKeysError from '@/components/api-keys/error'
import { DataTable } from '@/components/data-table/data-table'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import useApiKeys from '@/hooks/api/api-keys/useApiKeys'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { KeyRound } from 'lucide-react'
import { FC, useMemo } from 'react'

const ApiKeysPage: FC = () => {
  const { isLoading, error, apiKeys } = useApiKeys()
  const columns = useMemo(() => apiKeysColumns, [])

  let pageContent = <></>

  if (isLoading) {
    pageContent = <div>Loading...</div>
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
    <PageLayout>
      <div className="gap-4 m-6">
        <ContentBox className="w-fit min-w-[35vw] max-w-[50vw] min-h-[50vh] max-h-[50vh]">
          <div className="flex items-center gap-2">
            <KeyRound size={20} strokeWidth={2.5} />
            <h1 className="font-semibold">API Keys</h1>
          </div>
          <div className="grow overflow-auto">{pageContent}</div>
        </ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(ApiKeysPage)
