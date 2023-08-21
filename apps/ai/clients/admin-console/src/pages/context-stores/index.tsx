import PageLayout from '@/components/layout/page-layout'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC } from 'react'

const ContextStoresPage: FC = () => (
  <PageLayout>
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>Under construction...</h1>
    </main>
  </PageLayout>
)

export default withPageAuthRequired(ContextStoresPage)
