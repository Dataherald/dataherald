import React, { ReactNode, createContext, useContext, useState } from 'react'

export enum ESubscriptionErrorCode {
  no_payment_method = 'no_payment_method',
  spending_limit_exceeded = 'spending_limit_exceeded',
  hard_spending_limit_exceeded = 'hard_spending_limit_exceeded',
  subscription_past_due = 'subscription_past_due',
  subscription_canceled = 'subscription_canceled',
  unknown_subscription_status = 'unknown_subscription_status',
}

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

export const isSubscriptionErrorCode = (
  errorCode: string,
): errorCode is ESubscriptionErrorCode => {
  return Object.values(ESubscriptionErrorCode).includes(
    errorCode as ESubscriptionErrorCode,
  )
}
