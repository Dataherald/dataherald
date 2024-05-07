import ApiKeysList from '@/components/api-keys/api-keys-list'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import Head from 'next/head'
import { FC } from 'react'

const ApiKeysPage: FC = () => {
  return (
    <PageLayout>
      <Head>
        <title>API keys - Dataherald API</title>
      </Head>
      <div className="flex flex-col gap-4 m-6 max-w-2xl">
        <div className="flex flex-col gap-3">
          <p>
            {`Your secret API keys are listed below. Please note that we do not
            display your secret API keys again after you generate them.`}
          </p>
          <p>
            {`Do not share your API key with others, or expose it in the browser or
          other client-side code.`}
          </p>
        </div>
        <ContentBox className="w-100 min-h-[50vh]">
          <ApiKeysList />
        </ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(ApiKeysPage)
