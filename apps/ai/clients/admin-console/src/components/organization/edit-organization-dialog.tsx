import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
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
import { yupResolver } from '@hookform/resolvers/yup'
import { DialogClose, DialogTrigger } from '@radix-ui/react-dialog'
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
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description: 'The organization name could not be updated.',
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
        <Button variant="link" className="text-slate-900 p-0 h-fit">
          <Edit size={18} />
        </Button>
      </DialogTrigger>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleEditOrganization)}
            className="space-y-6 grow flex flex-col"
          >
            <DialogHeader>
              <h1 className="font-semibold">Organization Name</h1>
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
                <Button
                  type="button"
                  variant="secondary-outline"
                  disabled={saving}
                >
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
