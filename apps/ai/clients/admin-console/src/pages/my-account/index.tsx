import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { useAppContext } from '@/contexts/app-context'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { UserRound } from 'lucide-react'
import Head from 'next/head'
import { FC } from 'react'

const MyAccountPage: FC = () => {
  const { user, organization } = useAppContext()

  if (!user) return null

  return (
    <PageLayout>
      <Head>
        <title>My account - Dataherald AI API</title>
      </Head>
      {user && (
        <div className="grid grid-cols-2 gap-4 m-6">
          <ContentBox>
            <div className="flex items-center gap-2">
              <UserRound size={20} strokeWidth={2.5} />
              <h1 className="font-bold">Profile</h1>
            </div>
            {[
              { label: 'Name', value: user.name },
              { label: 'Email', value: user.email },
              { label: 'Role', value: user.role, hide: !user.role },
              {
                label: 'Organization',
                value: organization?.name,
              },
            ]
              .filter((v) => !v.hide)
              .map(({ label, value }, idx) => (
                <div key={idx} className="grid grid-cols-3 text-slate-800">
                  <span>{label}</span>
                  <span className="font-semibold">{value || '-'}</span>
                </div>
              ))}
          </ContentBox>
        </div>
      )}
    </PageLayout>
  )
}

export default withPageAuthRequired(MyAccountPage)
