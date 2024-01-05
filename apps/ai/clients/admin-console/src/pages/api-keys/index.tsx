import ApiKeys from '@/components/api-keys/api-keys'
import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC } from 'react'

const ApiKeysPage: FC = () => {
  return (
    <PageLayout>
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
        <ContentBox className="w-100 min-h-[50vh] max-h-[50vh]">
          <ApiKeys />
        </ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(ApiKeysPage)
