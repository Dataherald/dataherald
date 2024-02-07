import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
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
import { TableResource } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Edit, Loader } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const TABLE_DESCRIPTION_MAX_LENGTH = 500

const formSchema = Yup.object({
  description: Yup.string().max(
    TABLE_DESCRIPTION_MAX_LENGTH,
    `Maximum ${TABLE_DESCRIPTION_MAX_LENGTH} characters are allowed`,
  ),
})
interface TableResourceComponentProps {
  resource: TableResource
  onCancel: () => void
  onSave: (newDescription: string) => Promise<void>
}

const TableResourceComponent: FC<TableResourceComponentProps> = ({
  resource,
  onCancel,
  onSave,
}) => {
  const { icon, name } = resource

  const [isSaving, setIsSaving] = useState(false)
  const [editEnabled, setEditEnabled] = useState(!resource.description)

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
        className="space-y-3 grow flex flex-col"
      >
        <div className="grow flex flex-col">
          <SheetHeader>
            <SheetTitle>Add Text Description</SheetTitle>
            <div className="flex items-center gap-3 py-2">
              {renderIcon(icon, {
                size: 20,
              })}
              <span className="font-medium">{name}</span>
            </div>
          </SheetHeader>
          <SheetDescription>
            Text descriptions help instruct the AI on how to use a specific
            table.
          </SheetDescription>

          <div className="mt-2 flex items-center justify-between gap-2">
            <FormLabel>Table description</FormLabel>
            <Button
              variant="link"
              type="button"
              className="text-sm text-black flex items-center gap-1 px-0"
              onClick={() => setEditEnabled(true)}
            >
              <Edit size={14} strokeWidth={2}></Edit>
              Edit
            </Button>
          </div>
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem className="grow">
                <FormControl>
                  <Textarea
                    className="resize-none"
                    rows={10}
                    {...field}
                    disabled={!editEnabled}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <SheetFooter className="w-full flex sm:justify-between">
          <Button variant="ghost" type="button" onClick={onCancel}>
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

export default TableResourceComponent
