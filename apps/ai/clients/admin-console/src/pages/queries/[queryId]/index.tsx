import QueryLayout from '@/components/query/layout'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/useQuery'
import { executeQuery } from '@/hooks/api/useQueryExecution' // Import the custom fetch hook
import { Query } from '@/models/api'
import { useRouter } from 'next/router'
import { FC, useEffect, useState } from 'react'

const QueryPage: FC = () => {
  const router = useRouter()
  const { queryId } = router.query
  const {
    query: initialQuery,
    isLoading: isLoadingInitialQuery,
    error,
  } = useQuery(queryId as string)
  const [query, setQuery] = useState<Query | undefined>(initialQuery)

  useEffect(() => setQuery(initialQuery), [initialQuery])

  const handleExecuteQuery = async (sql_query: string) => {
    const newQuery = await executeQuery(queryId as string, sql_query)
    setQuery(newQuery)
  }

  let pageContent: JSX.Element = <></>

  if (isLoadingInitialQuery && !query) pageContent = <LoadingQuery />
  else if (error) pageContent = <div>Error loading the query</div>
  else if (query)
    pageContent = (
      <QueryWorkspace
        query={query as Query}
        onExecuteQuery={handleExecuteQuery}
      />
    )

  return <QueryLayout>{pageContent}</QueryLayout>
}

export default QueryPage
