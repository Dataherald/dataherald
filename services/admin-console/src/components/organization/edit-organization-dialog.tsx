import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import { useAppContext } from '@/contexts/app-context'
import { usePutOrganization } from '@/hooks/api/organization/usePutOrganization'
import { ErrorResponse } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { Edit, Loader } from 'lucide-react'
import { FC, useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const organizationFormSchema = Yup.object({
  name: Yup.string().required(`The Organization name can't be empty`),
})

type OrganizationFormValues = Yup.InferType<typeof organizationFormSchema>

const EditOrganizationDialog: FC = () => {
  const [saving, setSaving] = useState(false)
  const editOrganization = usePutOrganization()
  const { organization, updateOrganization: fetchContextOrg } = useAppContext()
  const form = useForm<OrganizationFormValues>({
    resolver: yupResolver(organizationFormSchema),
    defaultValues: {
      name: organization?.name || '',
    },
  })

  const handleCancel = (open: boolean) => {
    if (open) return
    form.reset({ name: organization?.name })
  }

  useEffect(() => {
    if (!organization) return
    form.reset({ name: organization?.name })
  }, [form, organization])

  const handleEditOrganization = async (
    organizationFormValues: OrganizationFormValues,
  ) => {
    if (!organization) return
    setSaving(true)
    try {
      await editOrganization(organization.id, {
        ...organization,
        ...organizationFormValues,
      })
      await fetchContextOrg()
      toast({
        variant: 'success',
        title: 'Organization name updated',
        description: `The organization name has been updated.`,
      })
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(handleEditOrganization)()}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog onOpenChange={handleCancel}>
      <DialogTrigger asChild>
        <Button variant="icon">
          <Edit size={14} />
        </Button>
      </DialogTrigger>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleEditOrganization)}
            className="space-y-6 grow flex flex-col"
          >
            <DialogHeader>
              <h1 className="font-semibold">Organization name</h1>
              <FormDescription>
                This is the name of your organization.
              </FormDescription>
            </DialogHeader>
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input {...field} disabled={saving} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="ghost" disabled={saving}>
                  Cancel
                </Button>
              </DialogClose>
              <Button disabled={saving}>
                {saving ? (
                  <>
                    <Loader
                      className="mr-2 animate-spin"
                      size={20}
                      strokeWidth={2.5}
                    />{' '}
                    Saving...
                  </>
                ) : (
                  'Save'
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
      <Toaster />
    </Dialog>
  )
}

export default EditOrganizationDialog
