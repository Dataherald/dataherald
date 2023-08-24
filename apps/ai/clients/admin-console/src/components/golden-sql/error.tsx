import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const QueriesError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching your organization golden sql queries. Please try
  again later."
  />
)

export default QueriesError
