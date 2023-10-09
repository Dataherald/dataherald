import DatabaseConnection from '@/components/databases/database-connection'
import DatabaseDetails from '@/components/databases/database-details'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { TreeProvider } from '@/components/ui/tree-view-context'
import useDatabases from '@/hooks/api/useDatabases'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC, useEffect, useState } from 'react'

const DatabasesPage: FC = () => {
  const { databases, isLoading, error, mutate } = useDatabases()
  const [connectingDB, setConnectingDB] = useState<boolean>(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const refreshDatabases = async (optimisticData?: Databases) => {
    try {
      mutate(optimisticData)
    } catch (e) {
      setIsRefreshing(false)
    }
  }

  const handleRefresh = async (newData?: Databases) => {
    setIsRefreshing(true)
    await refreshDatabases(newData)
    setIsRefreshing(false)
  }

  const handleDatabaseConnectionFinish = () => {
    setConnectingDB(false)
  }

  useEffect(() => {
    if (!isLoading) {
      if (databases?.length === 0) {
        setConnectingDB(true)
      } else {
        setConnectingDB(false)
      }
    }
  }, [isLoading, databases, connectingDB])

  let pageContent: JSX.Element = <></>

  if (!isLoading && error) {
    pageContent = <DatabasesError />
  } else if (isLoading && !connectingDB && !isRefreshing) {
    pageContent = <LoadingDatabases />
  } else if (connectingDB) {
    pageContent = (
      <DatabaseConnection
        onConnected={refreshDatabases}
        onFinish={handleDatabaseConnectionFinish}
      />
    )
  } else {
    pageContent = (
      <TreeProvider>
        <DatabaseDetails
          databases={databases as Databases}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />
      </TreeProvider>
    )
  }
  return (
    <PageLayout>
      <ContentBox>{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
