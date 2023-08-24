import PageLayout from '@/components/layout/page-layout'
import QueryError from '@/components/query/error'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { ContentBox } from '@/components/ui/content-box'
import { useQuery } from '@/hooks/api/useQuery'
import useQueryExecution from '@/hooks/api/useQueryExecution'
import usePatchQuery from '@/hooks/api/useQueryPatch'
import { Query, QueryStatus } from '@/models/api'
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
  const patchQuery = usePatchQuery()
  const executeQuery = useQueryExecution()

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

  if (isLoadingInitialQuery && !query) {
    pageContent = <LoadingQuery />
  } else if (error) {
    pageContent = <QueryError />
  } else if (query)
    pageContent = (
      <QueryWorkspace
        query={query as Query}
        onExecuteQuery={handleExecuteQuery}
        onPatchQuery={handlePatchQuery}
      />
    )

  return (
    <PageLayout>
      <ContentBox>{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueryPage)
