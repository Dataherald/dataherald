import DatabaseConnection from '@/components/databases/database-connection'
import DatabaseDetails from '@/components/databases/database-details'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { GlobalTreeSelectionProvider } from '@/components/ui/tree-view-global-context'
import useDatabases from '@/hooks/api/useDatabases'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC, useEffect, useState } from 'react'

const DatabasesPage: FC = () => {
  const { databases, isLoading, error, mutate, updateDatabases } =
    useDatabases()
  const [connectingDB, setConnectingDB] = useState<boolean>(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const refreshDatabases = async (optimisticData?: Databases) => {
    setIsRefreshing(true)
    try {
      await mutate(optimisticData)
      setIsRefreshing(false)
    } catch (e) {
      setIsRefreshing(false)
    }
  }

  const handleRefresh = async (newDatabases?: Databases) => {
    await refreshDatabases(newDatabases ? newDatabases : undefined)
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
      <GlobalTreeSelectionProvider>
        <DatabaseDetails
          databases={databases as Databases}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
          onUpdateDatabasesData={updateDatabases}
        />
      </GlobalTreeSelectionProvider>
    )
  }
  return (
    <PageLayout>
      <ContentBox className="m-6">{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
