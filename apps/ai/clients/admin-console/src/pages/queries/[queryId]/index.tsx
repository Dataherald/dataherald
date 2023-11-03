import PageLayout from '@/components/layout/page-layout'
import QueryError from '@/components/query/error'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/query/useQuery'
import useQueryExecution from '@/hooks/api/query/useQueryExecution'
import useQueryPatch, {
  QueryPatchRequest,
} from '@/hooks/api/query/useQueryPatch'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
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
  const patchQuery = useQueryPatch()
  const executeQuery = useQueryExecution()

  useEffect(() => setQuery(initialQuery), [initialQuery])

  const handleExecuteQuery = async (sql_query: string) => {
    try {
      const executedQuery = await executeQuery(queryId as string, sql_query)
      setQuery(executedQuery)
    } catch (e) {
      console.error(e)
      throw e
    }
    return void 0
  }

  const handlePatchQuery = async (patches: QueryPatchRequest) => {
    try {
      const patchedQuery = await patchQuery(queryId as string, patches)
      mutate(patchedQuery)
      setQuery(patchedQuery)
    } catch (e) {
      console.error(e)
      throw e
    }
    return void 0
  }

  let pageContent: JSX.Element = <></>

  if (isLoadingInitialQuery && !query) {
    pageContent = <LoadingQuery />
  } else if (error) {
    pageContent = (
      <div className="m-6">
        <QueryError />
      </div>
    )
  } else if (query)
    pageContent = (
      <QueryWorkspace
        query={query as Query}
        onExecuteQuery={handleExecuteQuery}
        onPatchQuery={handlePatchQuery}
      />
    )

  return <PageLayout disableBreadcrumb>{pageContent}</PageLayout>
}

export default withPageAuthRequired(QueryPage)
