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
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import { useAppContext } from '@/contexts/app-context'
import usePutSpendingLimits from '@/hooks/api/billing/usePutSpendingLimits'
import { toCents, toDollars } from '@/lib/utils'
import { ErrorResponse, SpendingLimits } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { Loader } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

interface EditSpendingLimitDialogProps {
  spendingLimits: SpendingLimits
  onUpdated: () => void
}

const EditSpendingLimitDialog: FC<EditSpendingLimitDialogProps> = ({
  spendingLimits,
  onUpdated,
}) => {
  const [saving, setSaving] = useState(false)
  const editLimits = usePutSpendingLimits()
  const { organization } = useAppContext()

  const spendingLimitInDollars = Number(
    toDollars(spendingLimits.spending_limit),
  )
  const hardLimitInDollars = Number(
    toDollars(spendingLimits.hard_spending_limit),
  )

  const spendingLimitFormSchema = Yup.object({
    spending_limit: Yup.number()
      .transform((value) => (isNaN(value) ? undefined : value))
      .required(`The spending limit name can't be empty`)
      .min(1, 'The spending limit must be greater than 0')
      .max(
        hardLimitInDollars,
        `The spending limit can't be greater than hard limit of $${hardLimitInDollars}. To increase the limit, please contact support.`,
      ),
  })

  type SpendingLimitFormValues = Yup.InferType<typeof spendingLimitFormSchema>

  const form = useForm<SpendingLimitFormValues>({
    resolver: yupResolver(spendingLimitFormSchema),
    defaultValues: {
      spending_limit: spendingLimitInDollars,
    },
  })

  const handleCancel = (open: boolean) => {
    if (open) return
    form.reset({ spending_limit: spendingLimitInDollars })
  }

  const handleEditSpendingLimit = async (
    spendingLimitFormValues: SpendingLimitFormValues,
  ) => {
    if (!organization) return
    setSaving(true)
    try {
      await editLimits(organization.id, {
        spending_limit: toCents(spendingLimitFormValues.spending_limit),
      })
      onUpdated()
      toast({
        variant: 'success',
        title: 'Spending limit updated',
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
            onClick={() => form.handleSubmit(handleEditSpendingLimit)()}
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
        <Button>Increase limit</Button>
      </DialogTrigger>
      <DialogContent onInteractOutside={(e) => e.preventDefault()}>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleEditSpendingLimit)}
            className="space-y-6 grow flex flex-col"
          >
            <DialogHeader>
              <h1 className="font-semibold">Increase your spending limit</h1>
              <FormDescription>
                The spending limit is the maximum amount you can spend on a
                single billing cycle.
              </FormDescription>
            </DialogHeader>
            <FormField
              control={form.control}
              name="spending_limit"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Spending limit in US dollars ($)</FormLabel>
                  <FormControl>
                    <Input {...field} type="number" disabled={saving} />
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

export default EditSpendingLimitDialog
