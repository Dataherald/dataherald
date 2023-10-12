import { DatabaseResourceFormShape } from '@/components/databases/database-resource-sheet'
import {
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import {
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import { renderIcon } from '@/lib/utils'
import { DatabaseResource } from '@/models/domain'
import { FC } from 'react'
import { UseFormReturn } from 'react-hook-form'

interface TableResourceComponentProps {
  resource: DatabaseResource
  form: UseFormReturn<DatabaseResourceFormShape, unknown, undefined>
}

const TableResourceComponent: FC<TableResourceComponentProps> = ({
  resource,
  form,
}) => {
  const { icon, name } = resource
  return (
    <>
      <SheetHeader>
        <SheetTitle>Add Text Description</SheetTitle>
        <div className="flex items-center gap-3 py-2">
          {renderIcon(icon, {
            size: 20,
          })}
          <span className="font-medium">{name}</span>
        </div>
        <SheetDescription>
          Text descriptions help instruct the AI on how to use a specific table.
        </SheetDescription>
      </SheetHeader>
      <FormField
        control={form.control}
        name="resourceText"
        render={({ field }) => (
          <FormItem className="grow">
            <FormControl>
              <Textarea className="resize-none" rows={10} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  )
}

export default TableResourceComponent
