import PageLayout from '@/components/layout/page-layout'
import EditOrganizationDialog from '@/components/organization/edit-organization-dialog'
import LlmCredentialsConfig from '@/components/organization/llm-api-key'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import UserList from '@/components/user/user-list'
import { useAppContext } from '@/contexts/app-context'
import { ERole } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { ArrowLeftRight, Building2 } from 'lucide-react'
import Head from 'next/head'
import Link from 'next/link'
import { FC } from 'react'

const OrganizationSettingsPage: FC = () => {
  const { user, organization, updateOrganization } = useAppContext()

  if (!organization) return null

  const isAdmin = user?.role === ERole.ADMIN

  return (
    <PageLayout>
      <Head>
        <title>Organization - Dataherald AI API</title>
      </Head>
      <div className="flex flex-col gap-5 m-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Building2 size={20} />
            <h1 className="text-xl font-semibold mr-2">{organization.name}</h1>
            <EditOrganizationDialog />
          </div>
          {isAdmin && (
            <Link href="/change-organization">
              <Button size="sm" className="h-fit px-4 py-1.5">
                <ArrowLeftRight className="mr-2" size={14} />
                Change Organization
              </Button>
            </Link>
          )}
        </div>
        <div className="flex items-start gap-4">
          <ContentBox className="flex-1 min-h-[50vh] max-w-2xl">
            <UserList />
          </ContentBox>
          {false && (
            <ContentBox className="flex-1">
              <LlmCredentialsConfig onOrganizationUpdate={updateOrganization} />
            </ContentBox>
          )}
        </div>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(OrganizationSettingsPage)
