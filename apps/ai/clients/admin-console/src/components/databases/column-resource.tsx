import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import {
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import { renderIcon } from '@/lib/utils'
import { ColumnResource } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Loader } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const COLUMN_DESCRIPTION_MAX_LENGTH = 300

const formSchema = Yup.object({
  description: Yup.string().max(
    COLUMN_DESCRIPTION_MAX_LENGTH,
    `Maximum ${COLUMN_DESCRIPTION_MAX_LENGTH} characters are allowed`,
  ),
})
interface ColumnResourceComponentProps {
  resource: ColumnResource
  onCancel: () => void
  onSave: (newDescription: string) => Promise<void>
}

const ColumnResourceComponent: FC<ColumnResourceComponentProps> = ({
  resource,
  onCancel,
  onSave,
}) => {
  const { icon, name } = resource

  const [isSaving, setIsSaving] = useState(false)

  const form = useForm<{ description?: string }>({
    resolver: yupResolver(formSchema),
    defaultValues: {
      description: resource?.description || '',
    },
  })

  const handleSave = async (data: { description?: string }) => {
    setIsSaving(true)
    await onSave(data.description || '')
    setIsSaving(false)
  }
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(handleSave)}
        className="space-y-6 grow flex flex-col"
      >
        <SheetHeader>
          <SheetTitle>Add Text Description</SheetTitle>
          <div className="flex items-center gap-3 py-2">
            {renderIcon(icon, {
              size: 20,
            })}
            <span className="font-medium">{name}</span>
          </div>
          <SheetDescription>
            Text descriptions help instruct the AI on how to use a specific
            column.
          </SheetDescription>
        </SheetHeader>
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem className="grow">
              <FormControl>
                <Textarea className="resize-none" rows={10} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <SheetFooter className="w-full flex sm:justify-between">
          <Button variant="outline" type="button" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader
                  className="mr-2 animate-spin"
                  size={20}
                  strokeWidth={2.5}
                />{' '}
                Saving
              </>
            ) : (
              'Save'
            )}
          </Button>
        </SheetFooter>
      </form>
    </Form>
  )
}

export default ColumnResourceComponent
