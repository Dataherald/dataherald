import { TreeNode, TreeView } from '@/components/ui/tree-view'
import {
  formatTableSyncStatus,
  getDatabaseLogo,
  getDomainTableSyncStatusColors,
  getDomainTableSyncStatusIcon,
  isSyncEnabled,
} from '@/lib/domain/database'
import { cn, renderIcon } from '@/lib/utils'
import {
  BasicTableDescription,
  Database,
  DatabaseSchema,
  ETableSyncStatus,
} from '@/models/api'
import { formatDistanceStrict } from 'date-fns'
import { Columns3, DatabaseIcon, LucideIcon, Table2 } from 'lucide-react'
import { FC, useMemo } from 'react'

const renderTreeIcon = (icon: LucideIcon): JSX.Element =>
  renderIcon(icon, { size: 16, strokeWidth: 1.8 }) as JSX.Element

const buildSchemas = (
  schemas: string[],
  tables: BasicTableDescription[],
): DatabaseSchema[] =>
  schemas.map((schema) => ({
    name: schema,
    tables: tables.filter((table) => table.schema_name === schema),
  }))

const mapSchemasToTreeNode = (schemas: DatabaseSchema[]) => ({
  id: 'schemas-root',
  name: 'Schemas',
  type: 'schema',
  icon: renderTreeIcon(DatabaseIcon),
  clickable: false,
  defaultOpen: true,
  children: schemas.map((schema) => ({
    id: schema.name,
    type: 'schema',
    name: schema.name,
    icon: renderTreeIcon(DatabaseIcon),
    clickable: false,
    defaultOpen: true,
    children: [mapTableToTreeNode(schema.tables)],
  })),
})

const mapTableToTreeNode = (tables: BasicTableDescription[]): TreeNode => ({
  id: 'tables-root',
  name: 'Tables',
  type: 'table',
  icon: renderTreeIcon(Table2),
  clickable: false,
  defaultOpen: true,
  children: tables.map((table) => ({
    id: table.id,
    type: 'table',
    name: table.name,
    icon: renderTreeIcon(Table2),
    clickable: table.sync_status === ETableSyncStatus.SCANNED,
    selectable: isSyncEnabled(table.sync_status),
    slot: (
      <div
        className={cn(
          'flex items-center gap-3 min-w-fit px-5',
          getDomainTableSyncStatusColors(table.sync_status).text,
        )}
      >
        {table.last_sync && (
          <span className="text-slate-500">
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
            icon: renderTreeIcon(Columns3),
            clickable: false,
            children: table.columns.map((column) => ({
              id: table.id,
              type: 'column',
              name: column,
              icon: renderTreeIcon(Columns3),
              clickable: table.sync_status === ETableSyncStatus.SCANNED,
            })),
          },
        ]
      : [],
  })),
})

const mapDatabaseToTreeData = (database: Database): TreeNode => ({
  id: database.db_connection_id,
  type: 'database',
  name: database.db_connection_alias,
  icon: getDatabaseLogo({
    id: database.db_connection_id,
    alias: database.db_connection_alias,
    dialect: database.dialect,
  }),
  clickable: true,
  selectable: database.tables.some((table) => isSyncEnabled(table.sync_status)),
  defaultOpen: true,
  showId: true,
  children: [
    database.schemas
      ? mapSchemasToTreeNode(buildSchemas(database.schemas, database.tables))
      : mapTableToTreeNode(database.tables),
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
