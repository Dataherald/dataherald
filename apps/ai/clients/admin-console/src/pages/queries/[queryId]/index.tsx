import PageLayout from '@/components/layout/page-layout'
import QueryError from '@/components/query/error'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/query/useQuery'
import useQueryExecution from '@/hooks/api/query/useQueryExecution'
import useQueryPatch, {
  QueryPatchRequest,
} from '@/hooks/api/query/useQueryPatch'
import useQueryResubmit from '@/hooks/api/query/useQueryResubmit'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/router'
import { FC, useEffect, useState } from 'react'

const QueryPage: FC = () => {
  const router = useRouter()
  const { queryId } = router.query
  const {
    query: serverQuery,
    isLoading: isLoadingServerQuery,
    error,
    mutate,
  } = useQuery(queryId as string)
  const [query, setQuery] = useState<Query | undefined>(serverQuery)
  const resubmitQuery = useQueryResubmit()
  const patchQuery = useQueryPatch()
  const executeQuery = useQueryExecution()

  useEffect(() => {
    setQuery(serverQuery)
  }, [serverQuery])

  const handleResubmitQuery = async () => {
    return mutate(resubmitQuery(queryId as string))
  }

  const handleExecuteQuery = async (sql_query: string) => {
    return mutate(executeQuery(queryId as string, sql_query))
  }

  const handlePatchQuery = async (patches: QueryPatchRequest) => {
    return mutate(patchQuery(queryId as string, patches))
  }

  let pageContent: JSX.Element = <></>

  if (isLoadingServerQuery && !query) {
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
        query={query}
        onResubmitQuery={handleResubmitQuery}
        onExecuteQuery={handleExecuteQuery}
        onPatchQuery={handlePatchQuery}
      />
    )

  return <PageLayout disableBreadcrumb>{pageContent}</PageLayout>
}

export default withPageAuthRequired(QueryPage)
