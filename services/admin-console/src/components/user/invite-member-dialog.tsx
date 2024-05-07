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
import { ErrorResponse } from '@/models/api'
import { EUserErrorCode } from '@/models/errorCodes'
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
    } catch (e) {
      console.error(e)
      const {
        message: title,
        trace_id: description,
        error_code,
      } = e as ErrorResponse
      let action: JSX.Element | undefined
      if (
        ![
          EUserErrorCode.user_exists_in_org,
          EUserErrorCode.user_exists_in_other_org,
        ].includes(error_code as EUserErrorCode)
      ) {
        // should be able to retry if the error is not related to user already existing
        action = (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(handleInviteMember)()}
          >
            Try again
          </ToastAction>
        )
      }
      setError(title)
      toast({
        variant: 'destructive',
        title,
        description,
        action,
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
                  <ShieldAlert size={16} />
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
                  <AlertCircle size={16} />
                </div>
                <AlertDescription>
                  {`We currently don't have a notification system in place. Once
                  you invite a user, please notify them that they need to sign up to the console.`}
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
