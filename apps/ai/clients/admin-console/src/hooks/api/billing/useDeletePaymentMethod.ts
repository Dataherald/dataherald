import { API_URL } from '@/config'
import useDelete from '@/hooks/api/generics/useDelete'

type DeletePaymentMethodRequest = { payment_method_id: string }

export const useDeletePaymentMethod = () => {
  const deletePaymentMethod = useDelete<DeletePaymentMethodRequest>()
  return (organizationId: string, paymentMethodId: string) =>
    deletePaymentMethod(
      `${API_URL}/organizations/${organizationId}/invoices/payment-methods/${paymentMethodId}`,
    )
}
