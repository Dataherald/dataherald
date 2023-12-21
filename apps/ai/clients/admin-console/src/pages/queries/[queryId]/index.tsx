import PageLayout from '@/components/layout/page-layout'
import QueryError from '@/components/query/error'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/query/useQuery'
import useQueryExecution from '@/hooks/api/query/useQueryExecution'
import useQueryPut, { QueryPutRequest } from '@/hooks/api/query/useQueryPut'
import useQueryResubmit from '@/hooks/api/query/useQueryResubmit'
import { mapQuery } from '@/lib/domain/query'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/router'
import { FC, useEffect, useState } from 'react'

const QueryPage: FC = () => {
  const router = useRouter()
  const { queryId: promptId } = router.query
  const {
    query: serverQuery,
    isLoading: isLoadingServerQuery,
    error,
    mutate,
  } = useQuery(promptId as string)
  const [query, setQuery] = useState<Query | undefined>(serverQuery)
  const resubmitQuery = useQueryResubmit()
  const putQuery = useQueryPut()
  const executeQuery = useQueryExecution()

  useEffect(() => {
    setQuery(serverQuery && mapQuery(serverQuery))
  }, [serverQuery])

  const handleResubmitQuery = async () => {
    return mutate(resubmitQuery(promptId as string))
  }

  const handleExecuteQuery = async (sql_query: string) => {
    return mutate(executeQuery(promptId as string, sql_query))
  }

  const handleputQuery = async (puts: QueryPutRequest) => {
    return mutate(putQuery(promptId as string, puts))
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
        onPutQuery={handleputQuery}
      />
    )

  return <PageLayout disableBreadcrumb>{pageContent}</PageLayout>
}

export default withPageAuthRequired(QueryPage)
