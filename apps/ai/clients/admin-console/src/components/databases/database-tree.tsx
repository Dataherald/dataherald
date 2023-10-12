import { TreeNode, TreeView } from '@/components/ui/tree-view'
import {
  formatTableSyncStatus,
  getDomainTableSyncStatusColors,
  getDomainTableSyncStatusIcon,
  isSyncEnabled,
} from '@/lib/domain/database'
import { cn, renderIcon } from '@/lib/utils'
import { Database, ETableSyncStatus } from '@/models/api'
import { formatDistanceStrict } from 'date-fns'
import { Columns, DatabaseIcon, Table2 } from 'lucide-react'
import { FC, useMemo } from 'react'

const mapDatabaseToTreeData = (database: Database): TreeNode => ({
  id: database.db_connection_id,
  type: 'database',
  name: database.alias,
  icon: DatabaseIcon,
  clickable: true,
  selectable: database.tables.some((table) => isSyncEnabled(table.sync_status)),
  defaultOpen: true,
  children: [
    {
      id: 'tables-root',
      name: 'Tables',
      type: 'table',
      icon: Table2,
      clickable: false,
      defaultOpen: true,
      children: database.tables.map((table) => ({
        id: table.id,
        type: 'table',
        name: table.name,
        icon: Table2,
        clickable: table.sync_status === ETableSyncStatus.SYNCHRONIZED,
        selectable: isSyncEnabled(table.sync_status),
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
                id: 'column-root',
                type: 'column',
                name: 'Columns',
                icon: Columns,
                clickable: false,
                children: table.columns.map((column) => ({
                  id: table.id,
                  type: 'column',
                  name: column,
                  icon: Columns,
                  clickable:
                    table.sync_status === ETableSyncStatus.SYNCHRONIZED,
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
