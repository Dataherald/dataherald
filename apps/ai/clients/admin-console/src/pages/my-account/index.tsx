import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { useAppContext } from '@/contexts/app-context'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { User2 } from 'lucide-react'
import { FC } from 'react'

const MyAccountPage: FC = () => {
  const { user, organization } = useAppContext()

  if (!user || !organization) return null

  return (
    <PageLayout>
      {user && (
        <div className="grid grid-cols-2 gap-4 m-6">
          <ContentBox>
            <div className="flex items-center gap-2">
              <User2 size={18} strokeWidth={2.5} />
              <h1 className="font-bold">Profile</h1>
            </div>
            {[
              { label: 'Name', value: user.name },
              { label: 'Email', value: user.email },
              { label: 'Role', value: user.role, hide: !user.role },
              {
                label: 'Organization',
                value: organization.name,
              },
            ]
              .filter((v) => !v.hide)
              .map(({ label, value }, idx) => (
                <div key={idx} className="grid grid-cols-3 text-gray-700">
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
