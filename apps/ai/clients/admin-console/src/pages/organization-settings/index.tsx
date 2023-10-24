import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import UserList from '@/components/user/user-list'
import { useAppContext } from '@/contexts/app-context'
import { ERole } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { ArrowLeftRight, Building2 } from 'lucide-react'
import Link from 'next/link'
import { FC } from 'react'

const OrganizationSettingsPage: FC = () => {
  const { user, organization } = useAppContext()

  if (!organization) return null

  const isAdmin = user?.role === ERole.ADMIN

  return (
    <PageLayout>
      <div className="flex flex-col gap-5">
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2">
            <Building2 size={18} />
            <h1 className="text-lg font-semibold">{organization.name}</h1>
          </div>
          {isAdmin && (
            <Link href="/select-organization">
              <Button variant="ghost" size="sm">
                <ArrowLeftRight className="mr-2" size={14} />
                Change Organization
              </Button>
            </Link>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4 min-h-[30vh] max-h-[30vh]">
          <ContentBox className="grow">
            <UserList />
          </ContentBox>
        </div>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(OrganizationSettingsPage)
