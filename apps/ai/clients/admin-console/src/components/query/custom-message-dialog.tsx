import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { yupResolver } from '@hookform/resolvers/yup'
import { FC, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const CUSTOM_MESSAGE_MAX_LENGTH = 3000

export const customMessageFormSchema = Yup.object({
  customMessage: Yup.string()
    .max(
      CUSTOM_MESSAGE_MAX_LENGTH,
      `The response can't be longer than 3000 characters`,
    )
    .required('Please enter a response for the query'),
})

type CustomMessageFormValues = Yup.InferType<typeof customMessageFormSchema>

interface CustomMessageDialogProps {
  initialValue: string
  isOpen: boolean
  title: string | JSX.Element
  description: string
  onClose: (newCustomMessage?: string) => void
}

const CustomMessageDialog: FC<CustomMessageDialogProps> = ({
  initialValue,
  isOpen,
  title,
  description,
  onClose,
}) => {
  const form = useForm<CustomMessageFormValues>({
    resolver: yupResolver(customMessageFormSchema),
    defaultValues: {
      customMessage: initialValue,
    },
  })

  const handleCancel = () => {
    form.reset({ customMessage: initialValue })
    onClose()
  }
  const handleContinue = (formValues: CustomMessageFormValues) => {
    form.reset({ customMessage: initialValue })
    onClose(formValues.customMessage)
  }

  useEffect(
    () => form.reset({ customMessage: initialValue }),
    [form, initialValue],
  )

  return (
    <Dialog open={isOpen} onOpenChange={handleCancel}>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleContinue)}
            className="space-y-6"
          >
            <DialogHeader className="flex-none">
              <DialogTitle>{title}</DialogTitle>
              <DialogDescription className="text-muted-foreground">
                {description}
              </DialogDescription>
            </DialogHeader>
            <FormField
              control={form.control}
              name="customMessage"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Textarea {...field} rows={10} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button variant="ghost" type="button" onClick={handleCancel}>
                Cancel
              </Button>
              <Button type="submit">Save</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
export default CustomMessageDialog
