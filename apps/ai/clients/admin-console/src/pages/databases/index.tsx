import DatabaseConnection from '@/components/databases/database-connection'
import DatabaseConnectionFormDialog from '@/components/databases/database-connection-form-dialog'
import DatabaseDetails from '@/components/databases/database-details'
import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { GlobalTreeSelectionProvider } from '@/components/ui/tree-view-global-context'
import useDatabases from '@/hooks/api/useDatabases'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import Head from 'next/head'
import { FC, useEffect, useState } from 'react'

const DatabasesPage: FC = () => {
  const { databases, isLoading, error, mutate, updateDatabases } =
    useDatabases()
  const [isConnectingFirstDB, setIsConnectingFirstDB] = useState(false)
  const [isLoadingAfterFirstConnection, setIsLoadingAfterFirstConnection] =
    useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async (newDatabases?: Databases, refresh = true) => {
    setIsRefreshing(true)
    try {
      await mutate(newDatabases, refresh)
      setIsRefreshing(false)
    } catch (e) {
      setIsRefreshing(false)
    }
  }

  const handleFirstDBConnected = async () => {
    setIsLoadingAfterFirstConnection(true)
    try {
      await mutate()
      setIsLoadingAfterFirstConnection(false)
    } catch (e) {
      setIsLoadingAfterFirstConnection(false)
    }
  }

  const handleFirstConnectionFinish = () => {
    setIsConnectingFirstDB(false)
  }

  useEffect(() => {
    if (databases && databases.length === 0) {
      setIsConnectingFirstDB(true)
    }
  }, [databases])

  let pageContent: JSX.Element = <></>

  if (error) {
    pageContent = (
      <div className="m-6">
        <DatabasesError />
      </div>
    )
  } else if (
    (isLoading || isLoadingAfterFirstConnection) &&
    !isRefreshing &&
    !isConnectingFirstDB
  ) {
    pageContent = <LoadingDatabases />
  } else if (isConnectingFirstDB) {
    pageContent = (
      <DatabaseConnection
        onConnected={handleFirstDBConnected}
        onFinish={handleFirstConnectionFinish}
      />
    )
  } else if (databases && databases.length > 0) {
    pageContent = (
      <GlobalTreeSelectionProvider>
        <div className="grow flex flex-col gap-4 m-6">
          <div>
            <DatabaseConnectionFormDialog onConnected={handleRefresh} />
          </div>
          <ContentBox className="grow">
            <DatabaseDetails
              databases={databases as Databases}
              isRefreshing={isRefreshing}
              onRefresh={handleRefresh}
              onUpdateDatabasesData={updateDatabases}
            />
          </ContentBox>
        </div>
      </GlobalTreeSelectionProvider>
    )
  }
  return (
    <PageLayout>
      <>
        <Head>
          <title>Databases - Dataherald AI API</title>
        </Head>
        {pageContent}
      </>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
