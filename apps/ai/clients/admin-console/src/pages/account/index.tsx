import PageLayout from '@/components/layout/page-layout'
import { ContentBox } from '@/components/ui/content-box'
import { useAppContext } from '@/contexts/app-context'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { FC } from 'react'

const OrganizationSettingsPage: FC = () => {
  const { user, organization } = useAppContext()

  if (!user || !organization) return null

  return (
    <PageLayout>
      {user && (
        <div className="grid grid-cols-2 gap-4">
          <ContentBox>
            <h1 className="font-bold text-lg">My profile</h1>
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

export default withPageAuthRequired(OrganizationSettingsPage)
