import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { yupResolver } from '@hookform/resolvers/yup'
import { DialogDescription } from '@radix-ui/react-dialog'
import { Info } from 'lucide-react'
import { FC, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const CUSTOM_RESPONSE_MAX_LENGTH = 3000

export const customResponseFormSchema = Yup.object({
  customResponse: Yup.string()
    .max(
      CUSTOM_RESPONSE_MAX_LENGTH,
      `The response can't be longer than 3000 characters`,
    )
    .required('Please enter a response for the query'),
})

type CustomResponseFormValues = Yup.InferType<typeof customResponseFormSchema>

interface CustomResponseDialogProps {
  initialValue: string
  isOpen: boolean
  title: string | JSX.Element
  description: string
  onClose: (newCustomResponse?: string) => void
}

const CustomResponseDialog: FC<CustomResponseDialogProps> = ({
  initialValue,
  isOpen,
  title,
  description,
  onClose,
}) => {
  const form = useForm<CustomResponseFormValues>({
    resolver: yupResolver(customResponseFormSchema),
    defaultValues: {
      customResponse: initialValue,
    },
  })

  const handleCancel = () => {
    onClose()
    form.reset({ customResponse: initialValue })
  }
  const handleContinue = (formValues: CustomResponseFormValues) => {
    onClose(formValues.customResponse)
  }

  useEffect(
    () => form.reset({ customResponse: initialValue }),
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
              name="customResponse"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Textarea {...field} />
                  </FormControl>
                  <FormMessage />
                  <FormDescription className="flex items-start gap-1 pt-2">
                    <Info size={18} strokeWidth={2}></Info>
                    {`This message will be sent as the question's response to the Slack thread.`}
                  </FormDescription>
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button variant="outline" type="button" onClick={handleCancel}>
                Cancel
              </Button>
              <Button type="submit">Done</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
export default CustomResponseDialog
