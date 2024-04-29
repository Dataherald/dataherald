import AddPaymentMethodDialog from '@/components/billing/add-payment-method-dialog'
import LoadingList from '@/components/layout/loading-list'
import PageErrorMessage from '@/components/error/page-error-message'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { toast } from '@/components/ui/use-toast'
import { useAppContext } from '@/contexts/app-context'
import { useDeletePaymentMethod } from '@/hooks/api/billing/useDeletePaymentMethod'
import usePaymentMethods from '@/hooks/api/billing/usePaymentMethods'
import { ErrorResponse, PaymentMethod } from '@/models/api'
import { CreditCard, Loader, Trash2 } from 'lucide-react'

import CreditCardLogo from '@/components/billing/credit-card-logo'
import { AlertDescription } from '@/components/ui/alert'
import { useState } from 'react'

const PaymentMethodsList = () => {
  const { organization } = useAppContext()
  const { isLoading, paymentMethods, error, mutate } = usePaymentMethods()
  const [
    selectedPaymentMethodForDeletion,
    setSelectedPaymentMethodForDeletion,
  ] = useState<PaymentMethod | null>(null)
  const [deletingCard, setDeletingCard] = useState(false)
  const deletePaymentMethod = useDeletePaymentMethod()

  const handlePaymentMethodAdded = () => {
    return mutate()
  }

  const handleDeletePaymentMethod = async (pm: PaymentMethod) => {
    if (!organization || !pm.id) return
    setDeletingCard(true)
    try {
      await deletePaymentMethod(organization.id, pm.id)
      await mutate()
      setSelectedPaymentMethodForDeletion(null)
      toast({
        variant: 'success',
        title: 'Payment Method Removed',
        description: `The payment method ending in ${pm.last4} was removed from the Organization.`,
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
            onClick={() => handleDeletePaymentMethod(pm)}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setDeletingCard(false)
    }
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <CreditCard size={20} strokeWidth={2.5} />
        <h1 className="font-semibold">Payment Methods</h1>
      </div>
      {error ? (
        <PageErrorMessage
          message="Something went wrong while retrieving your payment methods."
          error={error}
        />
      ) : (
        <>
          <div className="text-slate-500">
            Your charges will be deducted from the default card shown below.
          </div>
          <div className="grow overflow-auto min-h-[100px]">
            {isLoading ? (
              <LoadingList length={2} />
            ) : paymentMethods?.length ? (
              <ul className="py-2 space-y-3">
                {paymentMethods
                  .sort(
                    (
                      a,
                      b, // Sort payment methods by default status
                    ) =>
                      a.is_default && b.is_default ? 0 : a.is_default ? -1 : 1,
                  )
                  .map((pm: PaymentMethod, idx) => {
                    const { brand, last4, is_default } = pm

                    return (
                      <li
                        key={idx}
                        className="flex items-center justify-between gap-2"
                      >
                        <div className="flex items-center gap-4 font-semibold">
                          <CreditCardLogo brand={brand} />
                          <span className="text-lg">
                            **** **** **** {last4}
                          </span>
                          {is_default && (
                            <Badge
                              variant="secondary"
                              className="w-fit p-2 py-0.5 h-fit text-sm"
                            >
                              default
                            </Badge>
                          )}
                        </div>
                        {paymentMethods.length > 1 && (
                          <AlertDialog
                            open={
                              selectedPaymentMethodForDeletion?.id === pm.id
                            }
                            onOpenChange={(open) =>
                              !open && setSelectedPaymentMethodForDeletion(null)
                            }
                          >
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() =>
                                setSelectedPaymentMethodForDeletion(pm)
                              }
                            >
                              <Trash2 size={16} strokeWidth={1.5} />
                            </Button>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle className="inline-block">
                                  Remove card
                                </AlertDialogTitle>
                                <div className="flex items-center gap-4">
                                  <CreditCardLogo brand={brand} />
                                  <span className="text-lg">
                                    **** **** **** {last4}
                                  </span>
                                </div>
                              </AlertDialogHeader>
                              <AlertDescription>
                                Are you sure you want to remove this payment
                                method?
                              </AlertDescription>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <Button
                                  variant="destructive"
                                  disabled={deletingCard}
                                  onClick={() => handleDeletePaymentMethod(pm)}
                                >
                                  {deletingCard ? (
                                    <>
                                      <Loader
                                        size={16}
                                        className="animate-spin mr-2"
                                      />
                                      Removing...
                                    </>
                                  ) : (
                                    'Remove'
                                  )}
                                </Button>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </li>
                    )
                  })}
              </ul>
            ) : (
              <div>No payment methods saved.</div>
            )}
          </div>
          <div className="self-end">
            <AddPaymentMethodDialog
              isDefaultPayment={!paymentMethods?.some((pm) => pm.is_default)}
              onPaymentMethodAdded={handlePaymentMethodAdded}
            />
          </div>
        </>
      )}
    </>
  )
}

export default PaymentMethodsList
