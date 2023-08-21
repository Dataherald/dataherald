import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const QueryError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching the query. Please try
  again later."
  />
)

export default QueryError
