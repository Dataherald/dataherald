import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const FineTunningsError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching the fine-tunning models. Please try
  again later."
  />
)

export default FineTunningsError
