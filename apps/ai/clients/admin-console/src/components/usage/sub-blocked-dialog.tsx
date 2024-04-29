import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { SubscriptionErrorCode } from '@/contexts/subscription-context'
import Image from 'next/image'
import { FC } from 'react'

import Link from 'next/link'

const ERROR_CODE_MESSAGES: Record<
  SubscriptionErrorCode,
  {
    header: JSX.Element | string
    body: JSX.Element
    callToAction: JSX.Element
  }
> = {
  no_payment_method: {
    header: 'No Payment Method',
    body: <p>Please add a payment method to continue using the service.</p>,
    callToAction: (
      <Link href="/billing">
        <Button>Go to Billing Settings</Button>
      </Link>
    ),
  },
  spending_limit_exceeded: {
    header: 'Spending Limit Exceeded',
    body: (
      <p>
        {`You've exceeded your spending limit. Please update your spending limit
         from the Usage page.`}
      </p>
    ),
    callToAction: (
      <Link href="/usage">
        <Button>Go to Usage</Button>
      </Link>
    ),
  },
  hard_spending_limit_exceeded: {
    header: 'Hard Spending Limit Exceeded',
    body: (
      <>
        <p>
          You have reached your hard spending limit. This limit is not
          customizable through the console.
        </p>
        <p>To increase it, please contact support.</p>
      </>
    ),
    callToAction: (
      <a
        href="mailto:support@dataherald.com"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Button>Contact Support</Button>
      </a>
    ),
  },
  subscription_past_due: {
    header: 'Subscription Past Due',
    body: (
      <p>
        Your subscription payment is past due. Please update your payment
        details to continue using the service.
      </p>
    ),
    callToAction: (
      <Link href="/billing">
        <Button>Go to Billing Settings</Button>
      </Link>
    ),
  },
  subscription_canceled: {
    header: 'Subscription Canceled',
    body: (
      <p>
        Your subscription has been canceled. Please contact support to
        reactivate your subscription.
      </p>
    ),
    callToAction: (
      <a
        href="mailto:support@dataherald.com"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Button>Contact Support</Button>
      </a>
    ),
  },
  unknown_subscription_status: {
    header: 'Subscription Issue',
    body: (
      <p>
        {`There's an issue with your subscription that needs immediate
          attention. Please contact support.`}
      </p>
    ),
    callToAction: (
      <a
        href="mailto:support@dataherald.com"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Button>Contact Support</Button>
      </a>
    ),
  },
}

interface SubscriptionBlockedDialogProps {
  subErrorCode: SubscriptionErrorCode
  onClose: () => void
}

const SubscriptionBlockedDialog: FC<SubscriptionBlockedDialogProps> = ({
  subErrorCode,
  onClose,
}) => {
  const { header, body, callToAction } = ERROR_CODE_MESSAGES[subErrorCode]
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        className="p-0 max-w-[60vw] h-[80vh]"
        onInteractOutside={(e) => e.preventDefault()}
      >
        <div className="grid grid-cols-2">
          <div className="p-8 bg-slate-100 rounded-ss-lg rounded-es-lg flex items-center justify-center">
            <Image
              priority
              src="/images/dh-logo-color.svg"
              alt="Dataherald Logo"
              width={250}
              height={50}
            />
          </div>
          <div className="p-8 flex flex-col gap-10">
            <DialogHeader>
              <DialogTitle className="text-2xl">{header}</DialogTitle>
            </DialogHeader>
            <div className="grow flex flex-col gap-3">{body}</div>
            <DialogFooter>
              <DialogClose asChild onClick={onClose}>
                {callToAction}
              </DialogClose>
            </DialogFooter>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default SubscriptionBlockedDialog
