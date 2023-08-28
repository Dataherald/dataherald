import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const DatabasesError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching your database details. Please try
  again later."
  />
)

export default DatabasesError
