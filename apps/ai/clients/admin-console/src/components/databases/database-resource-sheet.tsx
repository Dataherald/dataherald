import ColumnResourceComponent from '@/components/databases/column-resource'
import DatabaseResourceComponent from '@/components/databases/database-resource'
import LoadingDatabaseResource from '@/components/databases/loading-resource'
import TableResourceComponent from '@/components/databases/table-resource'
import { Button } from '@/components/ui/button'
import { Form } from '@/components/ui/form'
import { Sheet, SheetContent, SheetFooter } from '@/components/ui/sheet'
import { useTree } from '@/components/ui/tree-view-context'
import { toast } from '@/components/ui/use-toast'
import useDatabaseResourceFromTree from '@/hooks/database/useDatabaseResourceFromTree'
import { DatabaseResourceType } from '@/models/domain'
import { yupResolver } from '@hookform/resolvers/yup'
import { Loader } from 'lucide-react'
import { FC, useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const DB_INSTRUCTION_MAX_LENGTH = 500
const DESCRIPTION_MAX_LENGTH = 300

export type DatabaseResourceFormShape = {
  resourceText?: string
}

const formSchemas: {
  [key in DatabaseResourceType]: Yup.ObjectSchema<DatabaseResourceFormShape>
} = {
  database: Yup.object({
    resourceText: Yup.string().max(
      DB_INSTRUCTION_MAX_LENGTH,
      `Maximum ${DB_INSTRUCTION_MAX_LENGTH} characters are allowed`,
    ),
  }),
  table: Yup.object({
    resourceText: Yup.string().max(
      DESCRIPTION_MAX_LENGTH,
      `Maximum ${DESCRIPTION_MAX_LENGTH} characters are allowed`,
    ),
  }),
  column: Yup.object({
    resourceText: Yup.string().max(
      DESCRIPTION_MAX_LENGTH,
      `Maximum ${DESCRIPTION_MAX_LENGTH} characters are allowed`,
    ),
  }),
}

const DatabaseResourceSheet: FC = () => {
  const { setClickedRow } = useTree()
  const { isLoading, resource, updateResource } = useDatabaseResourceFromTree()
  const [isSaving, setIsSaving] = useState(false)

  // given the way the resource is updated by the hook, we need to keep track of the initial resource text
  const formTextRef = useRef<string | null>(null)

  const formConfig = resource
    ? {
        resolver: yupResolver(formSchemas[resource.type]),
        defaultValues: {
          resourceText: resource?.text || '',
        },
      }
    : {}
  const form = useForm<DatabaseResourceFormShape>(formConfig)

  const handleCancel = () => {
    setClickedRow(null)
    form.reset({ resourceText: resource?.text })
  }
  const handleSave = async () => {
    try {
      setIsSaving(true)
      await updateResource(form.getValues().resourceText as string)
      setClickedRow(null)
    } catch (e) {
      toast({
        title: 'Something went wrong',
        variant: 'destructive',
      })
    } finally {
      setIsSaving(false)
    }
  }

  const renderDatabaseResourceComponent = () => {
    switch (resource?.type) {
      case 'database':
        return <DatabaseResourceComponent resource={resource} form={form} />
      case 'table':
        return <TableResourceComponent resource={resource} form={form} />
      case 'column':
        return <ColumnResourceComponent resource={resource} form={form} />
      default:
        return null
    }
  }

  useEffect(() => {
    if (resource) {
      if (formTextRef.current !== resource.text) {
        form.setValue('resourceText', resource.text, {
          shouldValidate: false, // Avoid triggering validation
          shouldDirty: false, // Keep the field in its non-dirty state
        })
        formTextRef.current = resource.text
      }
    }
  }, [formTextRef, form, resource])

  return (
    <Sheet
      open={isLoading || !!resource}
      onOpenChange={(open) => !open && handleCancel()}
    >
      <SheetContent
        className="w-[500px] sm:max-w-[500px] flex flex-col"
        onInteractOutside={(e) => e.preventDefault()}
      >
        {isLoading ? (
          <LoadingDatabaseResource />
        ) : (
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(handleSave)}
              className="space-y-6 grow flex flex-col"
            >
              {renderDatabaseResourceComponent()}
              <SheetFooter className="w-full flex sm:justify-between">
                <Button variant="outline" type="button" onClick={handleCancel}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading || isSaving}>
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
        )}
      </SheetContent>
    </Sheet>
  )
}

export default DatabaseResourceSheet
