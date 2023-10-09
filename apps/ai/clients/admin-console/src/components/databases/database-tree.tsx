import {
  formatTableSyncStatus,
  getDomainTableSyncStatusColors,
  getDomainTableSyncStatusIcon,
  isSelectableByStatus,
} from '@/lib/domain/database'
import { cn, renderIcon } from '@/lib/utils'
import { Database } from '@/models/api'
import { formatDistanceStrict } from 'date-fns'
import { Columns, DatabaseIcon, Table2 } from 'lucide-react'
import { FC, useMemo } from 'react'
import { TreeNode, TreeView } from '../ui/tree-view'

const mapDatabaseToTreeData = (database: Database): TreeNode => ({
  id: database.db_connection_id,
  name: database.alias,
  icon: DatabaseIcon,
  selectable: database.tables.some((table) =>
    isSelectableByStatus(table.sync_status),
  ),
  defaultOpen: true,
  children: [
    {
      name: 'Tables',
      id: 'tables-root',
      icon: Table2,
      defaultOpen: true,
      children: database.tables.map((table) => ({
        id: table.name,
        name: table.name,
        icon: Table2,
        selectable: isSelectableByStatus(table.sync_status),
        slot: (
          <div
            className={cn(
              'flex items-center gap-3 min-w-fit px-5',
              getDomainTableSyncStatusColors(table.sync_status).text,
            )}
          >
            {table.last_sync && (
              <span className="text-gray-400">
                {formatDistanceStrict(new Date(table.last_sync), new Date(), {
                  addSuffix: true,
                })}
              </span>
            )}
            {renderIcon(getDomainTableSyncStatusIcon(table.sync_status), {
              size: 16,
              strokeWidth: 2,
            })}
            {formatTableSyncStatus(table.sync_status)}
          </div>
        ),
        children: table.columns?.length
          ? [
              {
                id: 'columns-root',
                name: 'Columns',
                icon: Columns,
                children: table.columns.map((column) => ({
                  id: column,
                  name: column,
                  icon: Columns,
                })),
              },
            ]
          : [],
      })),
    },
  ],
})

interface DatabaseTreeProps {
  database: Database
}

const DatabaseTree: FC<DatabaseTreeProps> = ({ database }) => {
  const databaseTree = useMemo(
    () => database && mapDatabaseToTreeData(database),
    [database],
  )
  return <>{databaseTree && <TreeView rootNode={databaseTree} />}</>
}

export default DatabaseTree
