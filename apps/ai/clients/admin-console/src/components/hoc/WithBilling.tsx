import { STRIPE_PUBLIC_KEY } from '@/config'
import { Elements, useStripe } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'
import { FC, ReactNode } from 'react'

// Make sure to call `loadStripe` outside of a component’s render to avoid
// recreating the `Stripe` object on every render.
if (!STRIPE_PUBLIC_KEY) {
  throw new Error('Missing Stripe public key')
}

const stripe = loadStripe(STRIPE_PUBLIC_KEY)

type WithBillingProps = {
  children: ReactNode
}

const WithBilling: FC<WithBillingProps> = ({ children }) => (
  <Elements
    stripe={stripe}
    options={{
      fonts: [
        {
          src: 'https://fonts.googleapis.com/css2?family=Lato:wght@100;300;400;700;900&display=swap',
          family: 'Lato, sans-serif',
        },
      ],
    }}
  >
    {children}
  </Elements>
)

export default WithBilling

export const useBilling = useStripe
