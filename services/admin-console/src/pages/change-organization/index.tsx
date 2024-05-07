import BackgroundPageLayout from '@/components/layout/background-page-layout'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useAppContext } from '@/contexts/app-context'
import useOrganizations from '@/hooks/api/organization/useOrganizations'
import { cn } from '@/lib/utils'
import { ERole, Organization } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Check, Loader } from 'lucide-react'
import Head from 'next/head'
import Image from 'next/image'
import { useRouter } from 'next/router'
import { FC, useCallback, useEffect, useState } from 'react'

const SelectOrganizationPage: FC = () => {
  const router = useRouter()
  const { user, organization, setAdminOrganization } = useAppContext()
  const [signingIn, setSigningIn] = useState(false)
  const { organizations, isLoading } = useOrganizations()
  const [selectedOrganization, setSelectedOrganization] =
    useState<Organization>()

  useEffect(() => {
    // load current organization as default selected value
    if (selectedOrganization) return // if already selected, do nothing
    if (organization) {
      setSelectedOrganization(organization)
    }
  }, [organization, selectedOrganization])

  useEffect(() => {
    if (user && user.role !== ERole.ADMIN) {
      router.push('/')
    }
  }, [router, user])

  const isSelected = useCallback(
    (organizationId: string) => selectedOrganization?.id === organizationId,
    [selectedOrganization],
  )

  const handleSignIn = useCallback(async () => {
    if (selectedOrganization) {
      try {
        setSigningIn(true)
        await setAdminOrganization(selectedOrganization.id)
        await router.push('/')
        setSigningIn(false)
      } catch (error) {
        console.error(`Error signing in: ${error}`)
      }
    }
  }, [router, selectedOrganization, setAdminOrganization])

  const handleCancel = useCallback(() => {
    router.push('/organization')
  }, [router])

  return (
    <BackgroundPageLayout>
      <Head>
        <title>Change Organization - Dataherald API</title>
      </Head>
      <div className="bg-white shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-lg">
        <div className="flex flex-col items-center gap-5 h-[60vh] sm:max-h-[60vh]">
          <Image
            priority
            className="my-2"
            src="/images/dh-logo-color.svg"
            alt="Background"
            width={250}
            height={50}
          />
          <h1 className="text-2xl font-bold text-secondary-dark">
            Change Organization
          </h1>
          <p className="text-sm text-slate-500">
            Select the organization you wish to manage
          </p>
          {isLoading ? (
            Array.from({ length: 4 }).map((_, idx) => (
              <Skeleton key={idx} className="w-full h-20" />
            ))
          ) : (
            <ul className="grow w-full overflow-auto">
              {organizations?.map((organization) => (
                <li key={organization.name}>
                  <button
                    disabled={signingIn}
                    onClick={() => setSelectedOrganization(organization)}
                    className={cn(
                      'text-slate-900 w-full cursor-pointer hover:bg-slate-100 px-8 py-4 flex justify-between items-center',
                      isSelected(organization.id)
                        ? 'font-semibold bg-slate-200 hover:bg-slate-200 text-secondary'
                        : '',
                    )}
                  >
                    {organization.name}
                    {isSelected(organization.id) && <Check />}
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="w-full flex items-center justify-between gap-2">
            <Button variant="ghost" onClick={handleCancel}>
              Cancel
            </Button>
            <Button
              variant="secondary"
              disabled={!selectedOrganization || signingIn}
              onClick={handleSignIn}
            >
              {signingIn ? (
                <>
                  <Loader
                    className="mr-2 animate-spin"
                    size={20}
                    strokeWidth={2.5}
                  />{' '}
                  Saving
                </>
              ) : (
                'Continue'
              )}
            </Button>
          </div>
        </div>
      </div>
    </BackgroundPageLayout>
  )
}

export default withPageAuthRequired(SelectOrganizationPage)
