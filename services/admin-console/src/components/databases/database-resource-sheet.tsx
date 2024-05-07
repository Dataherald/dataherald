import ColumnResourceComponent from '@/components/databases/column-resource'
import DatabaseResourceComponent from '@/components/databases/database-resource'
import LoadingDatabaseResource from '@/components/databases/loading-resource'
import TableResourceComponent from '@/components/databases/table-resource'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { useTree } from '@/components/ui/tree-view-context'
import useDatabaseResourceFromTree from '@/hooks/database/useDatabaseResourceFromTree'
import {
  ColumnResource,
  DatabaseResource,
  DatabaseResourceType,
  TableResource,
} from '@/models/domain'
import { FC } from 'react'

const DatabaseResourceSheet: FC = () => {
  const { setClickedRow } = useTree()
  const { isLoading, resource, updateResource } = useDatabaseResourceFromTree()

  if (!updateResource) return

  const handleCancel = () => {
    setClickedRow(null)
  }

  const handleSave = async (newText: string) => {
    await updateResource(newText)
    setClickedRow(null)
  }

  const renderDatabaseResourceComponent = (
    resourceType: DatabaseResourceType,
  ) => {
    switch (resourceType) {
      case 'database':
        return (
          <DatabaseResourceComponent
            resource={resource as DatabaseResource}
            onCancel={handleCancel}
            onSave={handleSave}
          />
        )
      case 'table':
        return (
          <TableResourceComponent
            resource={resource as TableResource}
            onCancel={handleCancel}
            onSave={handleSave}
          />
        )
      case 'column':
        return (
          <ColumnResourceComponent
            resource={resource as ColumnResource}
            onCancel={handleCancel}
            onSave={handleSave}
          />
        )
    }
  }

  return (
    <Sheet
      open={isLoading || !!resource}
      onOpenChange={(open) => !open && handleCancel()}
    >
      <SheetContent className="w-[500px] sm:max-w-[500px] flex flex-col">
        {isLoading ? (
          <LoadingDatabaseResource />
        ) : (
          resource && renderDatabaseResourceComponent(resource.type)
        )}
      </SheetContent>
    </Sheet>
  )
}

export default DatabaseResourceSheet
