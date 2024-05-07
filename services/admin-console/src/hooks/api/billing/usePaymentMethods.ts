import { API_URL } from '@/config'
import { useAppContext } from '@/contexts/app-context'
import { useAuth } from '@/contexts/auth-context'
import { ErrorResponse, PaymentMethods } from '@/models/api'
import useSWR, { KeyedMutator } from 'swr'

interface PaymentMethodsResponse {
  paymentMethods: PaymentMethods | undefined
  isLoading: boolean
  error: ErrorResponse | null
  mutate: KeyedMutator<PaymentMethods>
}

const usePaymentMethods = (): PaymentMethodsResponse => {
  const { token } = useAuth()
  const { organization } = useAppContext()
  const endpointUrl = `${API_URL}/organizations/${organization?.id}/invoices/payment-methods`
  const { data, isLoading, error, mutate } = useSWR<PaymentMethods>(
    token && organization ? endpointUrl : null,
  )
  return {
    paymentMethods: data,
    isLoading: isLoading || (!data && !error),
    error,
    mutate,
  }
}

export default usePaymentMethods
