import PageLayout from '@/components/layout/page-layout'
import LlmCredentialsConfig from '@/components/organization/llm-api-key'
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
  const { user, organization, updateOrganization } = useAppContext()

  if (!organization) return null

  const isAdmin = user?.role === ERole.ADMIN

  return (
    <PageLayout>
      <div className="flex flex-col gap-5 m-6">
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
        <div className="flex items-start gap-4">
          <ContentBox className="flex-1 min-h-[50vh] max-h-[50vh]">
            <UserList />
          </ContentBox>
          <ContentBox className="flex-1">
            <LlmCredentialsConfig onOrganizationUpdate={updateOrganization} />
          </ContentBox>
        </div>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(OrganizationSettingsPage)
