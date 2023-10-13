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
import { DatabaseResource } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Edit, Loader } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const DB_INSTRUCTION_MAX_LENGTH = 500

const formSchema = Yup.object({
  instructions: Yup.string().max(
    DB_INSTRUCTION_MAX_LENGTH,
    `Maximum ${DB_INSTRUCTION_MAX_LENGTH} characters are allowed`,
  ),
})

interface DatabaseResourceProps {
  resource: DatabaseResource
  onCancel: () => void
  onSave: (newInstructions: string) => Promise<void>
}

const DatabaseResourceComponent: FC<DatabaseResourceProps> = ({
  resource,
  onCancel,
  onSave,
}) => {
  const { icon, name } = resource
  const [isSaving, setIsSaving] = useState(false)
  const [editEnabled, setEditEnabled] = useState(!resource.instructions)

  const form = useForm<{ instructions?: string }>({
    resolver: yupResolver(formSchema),
    defaultValues: {
      instructions: resource?.instructions || '',
    },
  })

  const handleSave = async (data: { instructions?: string }) => {
    setIsSaving(true)
    await onSave(data.instructions || '')
    setIsSaving(false)
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(handleSave)}
        className="space-y-6 grow flex flex-col"
      >
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
        <div className="grow flex flex-col">
          <div className="flex items-center justify-between gap-2">
            <FormLabel>Database instructions</FormLabel>
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
            name="instructions"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Textarea
                    className="resize-none"
                    rows={15}
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

export default DatabaseResourceComponent
