import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const ApiKeysError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching your API keys. Please try
  again later."
  />
)

export default ApiKeysError
