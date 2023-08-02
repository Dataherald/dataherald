import QueryLayout from '@/components/query/layout'
import LoadingQuery from '@/components/query/loading'
import QueryWorkspace from '@/components/query/workspace'
import { useQuery } from '@/hooks/api/useQuery'
import { Query } from '@/models/api'
import { useRouter } from 'next/router'
import { FC } from 'react'

const QueryPage: FC = () => {
  const router = useRouter()
  const { queryId } = router.query

  const { query, isLoading, error } = useQuery(queryId as string)

  let pageContent: JSX.Element

  if (isLoading && !query) pageContent = <LoadingQuery />
  else if (error) pageContent = <div>Error loading the query</div>
  else pageContent = <QueryWorkspace query={query as Query} />

  return <QueryLayout>{pageContent}</QueryLayout>
}

export default QueryPage
