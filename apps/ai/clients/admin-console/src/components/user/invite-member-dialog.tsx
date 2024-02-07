import { Alert, AlertDescription } from '@/components/ui/alert'
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
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import { usePostUserToOrganization } from '@/hooks/api/user/usePostUserToOrganization'
import { yupResolver } from '@hookform/resolvers/yup'
import { AlertCircle, Loader, ShieldAlert } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const userFormSchema = Yup.object({
  email: Yup.string()
    .email(`The email address must be a valid email`)
    .required(`The email address is required`),
})

type UserFormValues = Yup.InferType<typeof userFormSchema>

interface InviteMemberDialogProps {
  open: boolean
  onInviteMember: () => void
  onCancel: () => void
}

const InviteMemberDialog: FC<InviteMemberDialogProps> = ({
  open,
  onInviteMember,
  onCancel,
}) => {
  const [error, setError] = useState<string>()
  const [invitingMember, setInvitingMember] = useState(false)
  const postUser = usePostUserToOrganization()
  const form = useForm<UserFormValues>({
    resolver: yupResolver(userFormSchema),
    defaultValues: {
      email: '',
    },
  })

  const handleCancel = () => {
    form.reset()
    onCancel()
  }

  const handleInviteMember = async (userFormValues: UserFormValues) => {
    setInvitingMember(true)
    try {
      await postUser(userFormValues)
      form.reset()
      toast({
        variant: 'success',
        title: 'Member Invited',
        description: `The new member is now part of your Organization.`,
      })
      onInviteMember()
      setError(undefined)
    } catch (error) {
      let errorDescription: string
      let toastAction: JSX.Element | undefined
      const errorResponse = error as Error
      console.error(`Error adding user: ${errorResponse}`)
      if (errorResponse.cause === 409) {
        switch (errorResponse.message) {
          case 'USER_ALREADY_EXISTS_IN_ORG':
            errorDescription = `The user is already a member of your Organization.`
            break
          case 'USER_ALREADY_EXISTS_IN_OTHER_ORG':
            errorDescription = `The user is already a member of another Organization.`
            break
          default:
            errorDescription = `There was a problem inviting the new member to the Organization.`
        }
      } else {
        errorDescription = `There was a problem inviting the new member to the Organization.`
        toastAction = (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(handleInviteMember)()}
          >
            Try again
          </ToastAction>
        )
      }
      setError(errorDescription)
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description: errorDescription,
        action: toastAction,
      })
    } finally {
      setInvitingMember(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleCancel}>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleInviteMember)}
            className="space-y-8 grow flex flex-col"
          >
            <DialogHeader>
              <h1 className="font-semibold">Invite Team Member</h1>
              <FormDescription>
                Invite new member by email address
              </FormDescription>
            </DialogHeader>
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email Address</FormLabel>
                  <FormControl>
                    <Input {...field} disabled={invitingMember} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {error ? (
              <Alert variant="destructive" className="flex items-start gap-2">
                <div>
                  <ShieldAlert size={18} />
                </div>
                <AlertDescription>
                  {error} Please{' '}
                  <a
                    className="font-bold hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                    href="mailto:support@dataherald.com"
                  >
                    contact us
                  </a>{' '}
                  for assistance.
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="info" className="flex items-start gap-2">
                <div>
                  <AlertCircle size={18} />
                </div>
                <AlertDescription>
                  {`We currently don't have a notification system in place. Once
                  you invite a user, please notify them that they can
                  complete the sign up process by signing in here.`}
                </AlertDescription>
              </Alert>
            )}
            <DialogFooter>
              <Button
                type="button"
                variant="ghost"
                disabled={invitingMember}
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button>
                {invitingMember ? (
                  <>
                    <Loader
                      className="mr-2 animate-spin"
                      size={20}
                      strokeWidth={2.5}
                    />{' '}
                    Inviting member...
                  </>
                ) : (
                  'Invite'
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

export default InviteMemberDialog
