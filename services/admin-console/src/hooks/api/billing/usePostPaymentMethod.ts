import { API_URL } from '@/config'
import usePost from '@/hooks/api/generics/usePost'
import { PaymentMethod } from '@/models/api'

type PostPaymentMethodRequest = { payment_method_id: string }

export const usePostPaymentMethod = () => {
  const postPaymentMethod = usePost<PostPaymentMethodRequest, PaymentMethod>()
  return (
    organizationId: string,
    resource: PostPaymentMethodRequest,
    isDefault = true,
  ) => {
    return postPaymentMethod(
      `${API_URL}/organizations/${organizationId}/invoices/payment-methods?default=${isDefault}`,
      resource,
    )
  }
}
