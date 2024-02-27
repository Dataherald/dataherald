import { ESubscriptionErrorCode } from '@/models/errorCodes'
import React, { ReactNode, createContext, useContext, useState } from 'react'

export type SubscriptionErrorCode = keyof typeof ESubscriptionErrorCode

interface SubscriptionContextType {
  subscriptionStatus: SubscriptionErrorCode | null
  setSubscriptionStatus: (status: SubscriptionErrorCode | null) => void
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(
  undefined,
)

interface SubscriptionProviderProps {
  children: ReactNode
}

export const SubscriptionProvider: React.FC<SubscriptionProviderProps> = ({
  children,
}) => {
  const [subscriptionStatus, setSubscriptionStatus] =
    useState<SubscriptionErrorCode | null>(null)

  return (
    <SubscriptionContext.Provider
      value={{ subscriptionStatus, setSubscriptionStatus }}
    >
      {children}
    </SubscriptionContext.Provider>
  )
}

export const useSubscription = () => {
  const context = useContext(SubscriptionContext)
  if (context === undefined) {
    throw new Error(
      'useSubscription must be used within a SubscriptionProvider',
    )
  }
  return context
}
