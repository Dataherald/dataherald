import DatabaseConnection from '@/components/databases/database-connection'
import DatabaseDetails from '@/components/databases/database-details'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import useDatabases from '@/hooks/api/useDatabases'
import { Database, Databases } from '@/models/api'
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

  const handleRefresh = async (newDatabase?: Database) => {
    setIsRefreshing(true)
    await refreshDatabases(newDatabase ? [newDatabase] : undefined)
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
      <DatabaseDetails
        database={(databases as Databases)[0]} // Assuming only one database for now
        isRefreshing={isRefreshing}
        onRefresh={handleRefresh}
      />
    )
  }
  return (
    <PageLayout>
      <ContentBox className="m-6">{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
