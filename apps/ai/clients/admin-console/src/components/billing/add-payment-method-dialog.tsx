import WithBilling, { useBilling } from '@/components/hoc/WithBilling'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { toast } from '@/components/ui/use-toast'
import { useAppContext } from '@/contexts/app-context'
import { usePostPaymentMethod } from '@/hooks/api/billing/usePostPaymentMethod'
import { ErrorResponse, PaymentMethods } from '@/models/api'
import { CardElement, useElements } from '@stripe/react-stripe-js'
import { Loader, Plus } from 'lucide-react'
import { ComponentType, FC, FormEvent, useState } from 'react'

export interface AddPaymentMethodDialogProps {
  onPaymentMethodAdded: () => Promise<PaymentMethods | undefined>
  isDefaultPayment: boolean
}

const AddPaymentMethodDialog: FC<AddPaymentMethodDialogProps> = ({
  onPaymentMethodAdded,
  isDefaultPayment,
}) => {
  const billing = useBilling()
  const elements = useElements()
  const addPaymentMethod = usePostPaymentMethod()
  const { organization } = useAppContext()
  const [open, setOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [cardComplete, setCardComplete] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string>()

  const handleAddCard = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
    if (!organization) return
    if (!elements) return
    if (!billing) return
    if (!cardComplete) return
    setSaving(true)
    try {
      const result = await billing.createPaymentMethod({
        elements,
      })

      if (result.error) {
        console.error(result.error.message)
        setError(result.error.message)
      } else {
        try {
          const pmId = result.paymentMethod.id
          await addPaymentMethod(
            organization?.id,
            { payment_method_id: pmId },
            isDefaultPayment,
          )
          toast({
            variant: 'success',
            title: 'Payment method added',
            description: 'Your payment method has been added successfully.',
          })
          await onPaymentMethodAdded()
          reset()
        } catch (e) {
          console.error(e)
          const { message: title, trace_id: description } = e as ErrorResponse
          toast({
            variant: 'destructive',
            title,
            description,
          })
        }
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'An error occurred',
        description:
          'The payment method could not be added due to service provider error.',
      })
    } finally {
      setSaving(false)
    }
  }

  const reset = () => {
    setCardComplete(false)
    setSubmitted(false)
    setError('')
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && reset()}>
      <Button onClick={() => setOpen(true)}>
        <Plus size={16} className="mr-2" />
        Add new card
      </Button>
      <DialogContent
        onInteractOutside={(e) => e.preventDefault()}
        className="max-w-lg"
      >
        <form onSubmit={handleAddCard} className="flex flex-col space-y-5">
          <DialogHeader>
            <DialogTitle>Add new card</DialogTitle>
            <div className="text-slate-500 text-sm">
              Add a payment method for <strong>{organization?.name}</strong>
            </div>
          </DialogHeader>
          <div className="pt-5">
            <CardElement
              options={{
                style: {
                  base: { fontSize: '16px' },
                },
              }}
              onChange={(e) => setCardComplete(e.complete)}
            />
            <div className="text-destructive text-sm mt-3 h-5">
              {submitted &&
                !cardComplete &&
                !error &&
                'Please complete all the fields'}
              {error}
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" disabled={!billing || saving}>
              {saving ? (
                <>
                  <Loader size={20} className="animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                'Save'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

type WithBillingCmp = (
  Component: ComponentType<AddPaymentMethodDialogProps>,
) => React.FC<AddPaymentMethodDialogProps>

const withBilling: WithBillingCmp = (Component) => {
  return function WithAuthUser(
    props: AddPaymentMethodDialogProps,
  ): JSX.Element {
    return (
      <WithBilling>
        <Component {...props} />
      </WithBilling>
    )
  }
}

export default withBilling(AddPaymentMethodDialog)
