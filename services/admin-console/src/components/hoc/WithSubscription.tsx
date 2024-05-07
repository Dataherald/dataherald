import SubscriptionBlockedDialog from '@/components/usage/sub-blocked-dialog'
import { useSubscription } from '@/contexts/subscription-context'
import { FC, ReactNode } from 'react'

interface WithSubscriptionProps {
  children: ReactNode
}

const WithSubscription: FC<WithSubscriptionProps> = ({ children }) => {
  const { subscriptionStatus, setSubscriptionStatus } = useSubscription()

  return subscriptionStatus === null ? (
    <>{children}</>
  ) : (
    <>
      {children}
      <SubscriptionBlockedDialog
        subErrorCode={subscriptionStatus}
        onClose={() => setSubscriptionStatus(null)}
      ></SubscriptionBlockedDialog>
    </>
  )
}

export default WithSubscription
