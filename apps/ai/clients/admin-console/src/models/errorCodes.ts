export enum ESubscriptionErrorCode {
  no_payment_method = 'no_payment_method',
  spending_limit_exceeded = 'spending_limit_exceeded',
  hard_spending_limit_exceeded = 'hard_spending_limit_exceeded',
  subscription_past_due = 'subscription_past_due',
  subscription_canceled = 'subscription_canceled',
  unknown_subscription_status = 'unknown_subscription_status',
}

export enum EUserErrorCode {
  user_exists_in_org = 'user_exists_in_org',
  user_exists_in_other_org = 'user_exists_in_other_org',
}
