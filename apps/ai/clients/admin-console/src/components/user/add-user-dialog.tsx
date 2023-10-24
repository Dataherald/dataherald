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
import { usePostUser } from '@/hooks/api/user/usePostUser'
import { yupResolver } from '@hookform/resolvers/yup'
import { AlertCircle, Loader } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const userFormSchema = Yup.object({
  email: Yup.string()
    .email(`The email address must be a valid email`)
    .required(`The email address is required`),
})

type UserFormValues = Yup.InferType<typeof userFormSchema>

interface AddUserDialogProps {
  open: boolean
  onAddUser: () => void
  onCancel: () => void
}

const AddUserDialog: FC<AddUserDialogProps> = ({
  open,
  onAddUser,
  onCancel,
}) => {
  const [addingUser, setAddingUser] = useState(false)
  const postUser = usePostUser()
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

  const handleAddUser = async (userFormValues: UserFormValues) => {
    setAddingUser(true)
    try {
      await postUser(userFormValues)
      onAddUser()
      form.reset()
      toast({
        title: 'User added',
      })
    } catch (error) {
      console.error(`Error adding user: ${error}`)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem connecting your Database.',
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(handleAddUser)()}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setAddingUser(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleCancel}>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleAddUser)}
            className="space-y-8 grow flex flex-col"
          >
            <DialogHeader>
              <h1 className="font-semibold">Add User to the Organization</h1>
              <FormDescription>
                Grant access to a new user by entering their email address
              </FormDescription>
            </DialogHeader>
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email Address</FormLabel>
                  <FormControl>
                    <Input {...field} disabled={addingUser} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Alert variant="info" className="flex items-start gap-2">
              <div>
                <AlertCircle size={18} />
              </div>
              <AlertDescription>
                Once the user email address is added, they can sign in to the
                admin console and manage the organization
              </AlertDescription>
            </Alert>
            <DialogFooter>
              <Button
                type="button"
                variant="secondary-outline"
                disabled={addingUser}
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button>
                {addingUser ? (
                  <>
                    <Loader
                      className="mr-2 animate-spin"
                      size={20}
                      strokeWidth={2.5}
                    />{' '}
                    Adding user...
                  </>
                ) : (
                  'Add user'
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

export default AddUserDialog
