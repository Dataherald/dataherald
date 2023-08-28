import PageErrorMessage from '@/components/layout/page-error-message'
import { FC } from 'react'

const DatabaseError: FC = () => (
  <PageErrorMessage
    message="Something went wrong while fetching your database details. Please try
  again later."
  />
)

export default DatabaseError
