import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC } from 'react'

const DatabasesPage: FC = () => (
  <PageLayout>
    <ContentBox className="overflow-auto">Under Construction...</ContentBox>
  </PageLayout>
)

export default withPageAuthRequired(DatabasesPage)
