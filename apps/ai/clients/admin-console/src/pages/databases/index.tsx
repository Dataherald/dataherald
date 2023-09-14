import DatabasesError from '@/components/databases/error'
import LoadingDatabases from '@/components/databases/loading'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { TreeNode, TreeView } from '@/components/ui/tree-view'
import useDatabases from '@/hooks/api/useDatabases'
import { Databases } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Columns, Database as DatabaseIcon, Table2 } from 'lucide-react'
import { FC } from 'react'

const DatabasesPage: FC = () => {
  const { databases = [], isLoading, error } = useDatabases()

  const mapDatabaseToTreeData = (databases: Databases): TreeNode[] =>
    databases.map((database) => ({
      name: database.alias,
      icon: DatabaseIcon,
      children: [
        {
          name: 'Tables',
          icon: Table2,
          children: database.tables.map((table) => ({
            name: table.name,
            icon: Table2,
            children: [
              {
                name: 'Columns',
                icon: Columns,
                children: table.columns.map((column) => ({
                  name: column,
                  icon: Columns,
                })),
              },
            ],
          })),
        },
      ],
    }))

  let pageContent: JSX.Element = <></>

  if (error) {
    pageContent = <DatabasesError />
  } else if (isLoading) {
    pageContent = <LoadingDatabases />
  } else {
    pageContent = (
      <>
        <h1 className="capitalize font-semibold">Connected Databases</h1>
        <TreeView data={mapDatabaseToTreeData(databases as Databases)} />
      </>
    )
  }
  return (
    <PageLayout>
      <ContentBox>{pageContent}</ContentBox>
    </PageLayout>
  )
}

export default withPageAuthRequired(DatabasesPage)
