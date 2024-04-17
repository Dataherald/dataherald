import PageErrorMessage from '@/components/error/page-error-message'
import PageLayout from '@/components/layout/page-layout'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { ContentBox } from '@/components/ui/content-box'
import useQueries from '@/hooks/api/query/useQueries'
import { useQuery } from '@/hooks/api/query/useQuery'
import useQueryExecution from '@/hooks/api/query/useQueryExecution'
import useQueryPut, { QueryPutRequest } from '@/hooks/api/query/useQueryPut'
import useQueryResubmit from '@/hooks/api/query/useQueryResubmit'
import { mapQuery } from '@/lib/domain/query'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import Head from 'next/head'
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
  const { mutate: mutateListing } = useQueries()
  const [query, setQuery] = useState<Query | undefined>(undefined)
  const resubmitQuery = useQueryResubmit()
  const putQuery = useQueryPut()
  const executeQuery = useQueryExecution()

  useEffect(() => {
    // first update of the query from the server.
    // this server query should only be used to initialize the query state.
    // remaining updates are handled by each of the operations and not from the GET query endpoint.
    // this is because the GET query endpoint doesn't have `sql_result`.
    if (serverQuery)
      setQuery((prevState) =>
        prevState === undefined ? serverQuery : prevState,
      )
  }, [serverQuery])

  const handleQueryMutation = async () => {
    mutateListing()
    return mutate()
  }

  const handleResubmitQuery = async () => {
    const newQuery = await resubmitQuery(promptId as string)
    setQuery(newQuery)
    return handleQueryMutation()
  }

  const handleExecuteQuery = async (sql_query: string) => {
    const newQuery = await executeQuery(promptId as string, sql_query)
    setQuery(newQuery)
    return handleQueryMutation()
  }

  const handlePutQuery = async (updates: QueryPutRequest) => {
    const newQuery = await putQuery(promptId as string, updates)
    setQuery(newQuery)
    return handleQueryMutation()
  }

  const handleQueryUpdate = async () => {
    const newQuery = await handleQueryMutation()
    setQuery(newQuery)
  }

  let pageContent: JSX.Element = <></>
  if (isLoadingServerQuery && !query) {
    pageContent = <LoadingQuery />
  } else if (error) {
    pageContent = (
      <ContentBox className="m-6">
        <PageErrorMessage
          message="Something went wrong while fetching the query. Please try
          again later."
          error={error}
        />
      </ContentBox>
    )
  } else if (query)
    pageContent = (
      <QueryWorkspace
        query={mapQuery(query)}
        onResubmitQuery={handleResubmitQuery}
        onExecuteQuery={handleExecuteQuery}
        onPutQuery={handlePutQuery}
        onMessageSent={handleQueryUpdate}
      />
    )

  return (
    <PageLayout disableBreadcrumb>
      <>
        <Head>
          <title>Query editor - Dataherald API</title>
        </Head>
        {pageContent}
      </>
    </PageLayout>
  )
}

export default withPageAuthRequired(QueryPage)
