import { API_URL } from '@/config'
import usePut from '@/hooks/api/generics/usePut'

type PutLimitsRequest = { spending_limit: number }

const usePutSpendingLimits = () => {
  const putSpendingLimits = usePut<PutLimitsRequest>()
  return (organizationId: string, newLimits: PutLimitsRequest) => {
    return putSpendingLimits(
      `${API_URL}/organizations/${organizationId}/invoices/limits`,
      newLimits,
    )
  }
}

export default usePutSpendingLimits
