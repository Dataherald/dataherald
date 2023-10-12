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

interface DatabaseResourceProps {
  resource: DatabaseResource
  form: UseFormReturn<DatabaseResourceFormShape, unknown, undefined>
}

const DatabaseResourceComponent: FC<DatabaseResourceProps> = ({
  resource,
  form,
}) => {
  const { icon, name } = resource
  return (
    <>
      <SheetHeader>
        <SheetTitle>Add Database Instructions</SheetTitle>
        <div className="flex items-center gap-3 py-2">
          {renderIcon(icon, {
            size: 20,
          })}
          <span className="font-medium">{name}</span>
        </div>
        <SheetDescription>
          Database-level instructions are natural language directives you can
          give to the engine that will improve the agent’s performance.
        </SheetDescription>
      </SheetHeader>
      <FormField
        control={form.control}
        name="resourceText"
        render={({ field }) => (
          <FormItem className="grow">
            <FormControl>
              <Textarea className="resize-none" rows={15} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  )
}

export default DatabaseResourceComponent
