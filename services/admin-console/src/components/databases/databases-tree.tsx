import DatabaseResourceSheet from '@/components/databases/database-resource-sheet'
import DatabaseTree from '@/components/databases/database-tree'
import { TreeProvider } from '@/components/ui/tree-view-context'
import { Databases } from '@/models/api'
import { FC } from 'react'

interface DatabasesTreeProps {
  databases: Databases
}

const DatabasesTree: FC<DatabasesTreeProps> = ({ databases }) => {
  return (
    <div className="flex flex-col gap-0">
      {databases &&
        databases.map((database) => (
          <TreeProvider key={database.db_connection_id}>
            <DatabaseTree database={database} />
            <DatabaseResourceSheet />
          </TreeProvider>
        ))}
    </div>
  )
}

export default DatabasesTree
