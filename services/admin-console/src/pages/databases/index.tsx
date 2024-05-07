import DatabaseDetails from '@/components/databases/database-details'
import FirstDatabaseConnection from '@/components/databases/first-database-connection'
import LoadingDatabases from '@/components/databases/loading'
import PageErrorMessage from '@/components/error/page-error-message'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { GlobalTreeSelectionProvider } from '@/components/ui/tree-view-global-context'
import useDatabases from '@/hooks/api/database-connection/useDatabases'
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
      <ContentBox className="m-6">
        <PageErrorMessage
          message="Something went wrong while fetching your database details."
          error={error}
        />
      </ContentBox>
    )
  } else if (
    (isLoading || isLoadingAfterFirstConnection) &&
    !isRefreshing &&
    !isConnectingFirstDB
  ) {
    pageContent = <LoadingDatabases />
  } else if (isConnectingFirstDB) {
    pageContent = (
      <FirstDatabaseConnection
        onConnected={handleFirstDBConnected}
        onFinish={handleFirstConnectionFinish}
      />
    )
  } else if (databases && databases.length > 0) {
    pageContent = (
      <GlobalTreeSelectionProvider>
        <ContentBox className="grow m-6 gap-1">
          <DatabaseDetails
            databases={databases as Databases}
            isRefreshing={isRefreshing}
            onRefresh={handleRefresh}
            onUpdateDatabasesData={updateDatabases}
          />
        </ContentBox>
      </GlobalTreeSelectionProvider>
    )
  }

  return (
    <PageLayout>
      <>
        <Head>
          <title>Databases - Dataherald API</title>
        </Head>
        {pageContent}
      </>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
