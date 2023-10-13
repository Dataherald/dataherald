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
import { ColumnResource } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Brackets, Edit, Loader } from 'lucide-react'
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
  const { icon, name, categories } = resource

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
        className="space-y-6 grow flex flex-col overflow-auto"
      >
        <SheetHeader>
          <SheetTitle>Add Text Description</SheetTitle>
        </SheetHeader>
        <div className="grow flex flex-col gap-3 pl-2 pr-4 overflow-auto">
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
          <div className="flex flex-col">
            <div className="flex items-center justify-between gap-2">
              <FormLabel>Table description</FormLabel>
              <Button
                variant="link"
                type="button"
                className="text-sm text-black flex items-center gap-1"
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
                <FormItem>
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
          {categories?.length && (
            <div className="py-3 flex flex-col gap-3">
              <h1 className="font-semibold flex items-center gap-2">
                <Brackets size={20} strokeWidth={2} />
                Categorical Column detected
              </h1>
              <p className="text-sm">
                The AI has identified this as a categorical column with the
                following categories:
              </p>
              <ul className="grow list-disc list-inside space-y-2">
                {categories.map((category) => (
                  <li
                    key={category}
                    className="pl-3 text-sm font-source-code font-semibold"
                  >
                    {category}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
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
