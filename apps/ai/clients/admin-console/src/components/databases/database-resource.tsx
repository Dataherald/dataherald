import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { toast } from '@/components/ui/use-toast'
import { cn, copyToClipboard } from '@/lib/utils'
import { DatabaseResource } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Copy, Loader, Lock, LucideIcon, Unlock } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const DB_INSTRUCTION_MAX_LENGTH = 2000

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
  const { id, icon, name } = resource
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

  const handleCopyId = async () => {
    try {
      await copyToClipboard(id)
      toast({
        variant: 'success',
        title: 'Database ID copied!',
      })
    } catch (error) {
      console.error('Could not copy text: ', error)
      toast({
        variant: 'destructive',
        title: 'Could not copy the Database ID',
      })
    }
  }

  const EditIcon: LucideIcon = editEnabled ? Unlock : Lock

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(handleSave)}
        className="space-y-6 grow flex flex-col"
      >
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <icon.type {...icon.props} width={36} height={36} />
            <div className="flex flex-col">
              <div className="break-all">{name}</div>
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                ID {id}{' '}
                <Button
                  type="button"
                  variant="icon"
                  onClick={handleCopyId}
                  className="p-0 h-fit text-slate-500"
                >
                  <Copy size={12} strokeWidth={2.5} />
                </Button>
              </div>
            </div>
          </SheetTitle>
        </SheetHeader>
        <div className="grow flex flex-col gap-1">
          <div className="flex items-center justify-between gap-2">
            <FormLabel>Database instructions</FormLabel>
            <TooltipProvider>
              <Tooltip delayDuration={0}>
                <TooltipTrigger asChild>
                  <Button
                    variant="icon"
                    type="button"
                    className="p-0 h-fit"
                    onClick={() => setEditEnabled(!editEnabled)}
                  >
                    <EditIcon size={16} strokeWidth={2.5} />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <strong>Enable</strong> or <strong>disable</strong> editing
                  the database-level instructions
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <FormDescription className="mb-1">
            Database-level instructions are natural language directives you can
            give to the engine that will improve the agent’s performance.
          </FormDescription>
          <FormField
            control={form.control}
            name="instructions"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Textarea
                    className={cn(
                      'resize-none',
                      editEnabled ? 'bg-inherit' : 'bg-gray-100',
                    )}
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

export default DatabaseResourceComponent
