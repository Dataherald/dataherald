import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const QueriesError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching your organization queries. Please try
  again later."
  />
)

export default QueriesError
