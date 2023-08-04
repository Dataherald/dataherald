import QueryLayout from '@/components/query/layout'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/useQuery'
import { executeQuery } from '@/hooks/api/useQueryExecution' // Import the custom fetch hook
import { patchQuery } from '@/hooks/api/useQueryPatch'
import { Query, QueryStatus } from '@/models/api'
import { useRouter } from 'next/router'
import { FC, useEffect, useState } from 'react'

const QueryPage: FC = () => {
  const router = useRouter()
  const { queryId } = router.query
  const {
    query: initialQuery,
    isLoading: isLoadingInitialQuery,
    error,
    mutate,
  } = useQuery(queryId as string)
  const [query, setQuery] = useState<Query | undefined>(initialQuery)

  useEffect(() => setQuery(initialQuery), [initialQuery])

  const handleExecuteQuery = async (sql_query: string) => {
    const executedQuery = await executeQuery(queryId as string, sql_query)
    setQuery(executedQuery)
  }

  const handlePatchQuery = async (patches: {
    sql_query: string
    query_status: QueryStatus
  }) => {
    const patchedQuery = await patchQuery(queryId as string, patches)
    mutate(patchedQuery)
    setQuery(patchedQuery)
  }

  let pageContent: JSX.Element = <></>

  if (isLoadingInitialQuery && !query) pageContent = <LoadingQuery />
  else if (error) pageContent = <div>Error loading the query</div>
  else if (query)
    pageContent = (
      <QueryWorkspace
        query={query as Query}
        onExecuteQuery={handleExecuteQuery}
        onPatchQuery={handlePatchQuery}
      />
    )

  return <QueryLayout>{pageContent}</QueryLayout>
}

export default QueryPage
