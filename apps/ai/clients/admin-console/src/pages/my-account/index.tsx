import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { useAppContext } from '@/contexts/app-context'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { format } from 'date-fns'
import { UserRound } from 'lucide-react'
import Head from 'next/head'
import { FC, Fragment } from 'react'

const MyAccountPage: FC = () => {
  const { user, organization } = useAppContext()

  if (!user) return null

  const { name, email, role, created_at } = user

  return (
    <PageLayout>
      <Head>
        <title>My account - Dataherald API</title>
      </Head>
      {user && (
        <div className="m-6">
          <ContentBox className="grow max-w-fit">
            <div className="flex items-start gap-2">
              <UserRound size={20} strokeWidth={2.5} />
              <h1 className="font-semibold">Profile</h1>
            </div>
            <div className="grid grid-cols-[auto,1fr] gap-3 text-sm">
              {[
                { label: 'Name', value: name },
                { label: 'Email', value: email },
                { label: 'Role', value: role, hide: !role },
                {
                  label: 'Organization',
                  value: organization?.name,
                },
                {
                  label: 'Member since',
                  value: format(new Date(created_at), 'MMM dd, yyyy'),
                },
              ]
                .filter((v) => !v.hide)
                .map(({ label, value }, idx) => (
                  <Fragment key={idx}>
                    <span className="w-fit uppercase font-semibold tracking-wide mr-5">
                      {label}
                    </span>
                    <span className="text-slate-500 mr-5">{value || '-'}</span>
                  </Fragment>
                ))}
            </div>
          </ContentBox>
        </div>
      )}
    </PageLayout>
  )
}

export default withPageAuthRequired(MyAccountPage)
