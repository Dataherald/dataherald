import PageLayout from '@/components/layout/page-layout'
import EditOrganizationDialog from '@/components/organization/edit-organization-dialog'
import LlmApiKeyConfig from '@/components/organization/llm-api-key'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import { toast } from '@/components/ui/use-toast'
import UserList from '@/components/user/user-list'
import { useAppContext } from '@/contexts/app-context'
import { copyToClipboard } from '@/lib/utils'
import { ERole } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { ArrowLeftRight, Building2, Copy, UsersRound } from 'lucide-react'
import Head from 'next/head'
import Link from 'next/link'
import { FC, ReactNode } from 'react'

type OrganizationDisplayDetails = {
  label: string
  description: string
  value: string
  action: JSX.Element
}

const OrganizationSettingsPage: FC = () => {
  const { user, organization, updateOrganization } = useAppContext()

  if (!organization) return null

  const isAdmin = user?.role === ERole.ADMIN

  const handleCopyOrgId = async () => {
    try {
      await copyToClipboard(organization.id)
      toast({
        variant: 'success',
        title: 'Organization ID copied!',
      })
    } catch (error) {
      console.error('Could not copy text: ', error)
      toast({
        variant: 'destructive',
        title: 'Could not copy the Organization ID',
      })
    }
  }

  const ORGANIZATION_DETAILS_DISPLAY: OrganizationDisplayDetails[] = [
    {
      label: 'Organization name',
      description: 'Human-friendly label to display in user interfaces',
      value: organization.name,
      action: <EditOrganizationDialog />,
    },
    {
      label: 'Organization ID',
      description: 'Identifier for this organization used in API requests',
      value: organization.id,
      action: (
        <Button variant="icon" onClick={handleCopyOrgId}>
          <Copy size={14} />
        </Button>
      ),
    },
  ]

  const renderDetails: (details: OrganizationDisplayDetails[]) => ReactNode = (
    details,
  ) =>
    details.map(({ label, description, value, action }, index) => (
      <div key={index} className="flex flex-col gap-0.5">
        <div className="flex flex-col">
          <strong className="text-sm">{label}</strong>
          <p className="text-slate-500 text-xs">{description}</p>
        </div>
        <div className="flex items-center gap-3">
          <p className="text-slate-900">{value}</p>
          {action}
        </div>
      </div>
    ))

  return (
    <PageLayout>
      <Head>
        <title>Organization - Dataherald API</title>
      </Head>
      <div className="grow flex flex-col gap-5 m-6">
        {isAdmin && (
          <Link className="w-fit" href="/change-organization">
            <Button>
              <ArrowLeftRight className="mr-2" size={16} />
              Change Organization
            </Button>
          </Link>
        )}
        <div className="grow grid grid-cols-2 grid-rows-[auto,1fr] gap-6 max-w-4xl">
          <ContentBox>
            <div className="flex items-start gap-2">
              <Building2 size={20} strokeWidth={2.5} />
              <h1 className="font-semibold">Details</h1>
            </div>
            <div className="flex flex-col gap-4 pt-3">
              {renderDetails(ORGANIZATION_DETAILS_DISPLAY)}
            </div>
          </ContentBox>
          <ContentBox>
            <LlmApiKeyConfig onOrganizationUpdate={updateOrganization} />
          </ContentBox>
          <ContentBox className="col-span-2">
            <div className="flex items-start gap-2">
              <UsersRound size={20} strokeWidth={2.5} />
              <h1 className="font-semibold">Team</h1>
            </div>
            <UserList />
          </ContentBox>
        </div>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(OrganizationSettingsPage)
