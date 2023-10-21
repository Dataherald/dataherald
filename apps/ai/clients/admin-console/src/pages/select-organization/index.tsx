import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useAppContext } from '@/contexts/app-context'
import useOrganizations from '@/hooks/api/organization/useOrganizations'
import { cn } from '@/lib/utils'
import { Organization } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Check, Loader } from 'lucide-react'
import Image from 'next/image'
import { useRouter } from 'next/router'
import { FC, useCallback, useEffect, useState } from 'react'

const SelectOrganizationPage: FC = () => {
  const router = useRouter()
  const [signingIn, setSigningIn] = useState(false)
  const { organizations, isLoading } = useOrganizations()
  const [selectedOrganization, setSelectedOrganization] =
    useState<Organization>()

  const { selectingOrg, setAdminOrganization } = useAppContext()

  const isSelected = useCallback(
    (organizationId: string) => selectedOrganization?.id === organizationId,
    [selectedOrganization],
  )

  const handleSignIn = useCallback(async () => {
    if (selectedOrganization) {
      try {
        setSigningIn(true)
        await setAdminOrganization(selectedOrganization.id)
        setSigningIn(false)
      } catch (error) {
        console.error(`Error signing in: ${error}`)
      }
    }
  }, [selectedOrganization, setAdminOrganization])

  useEffect(() => {
    if (!selectingOrg) {
      router.push('/')
    }
  }, [router, selectingOrg])

  return (
    <div className="flex items-center justify-center min-h-screen relative">
      <Image
        src="https://hi-george.s3.amazonaws.com/DataheraldAI/Dark+Background.png"
        alt="Background"
        fill
        style={{ objectFit: 'cover', objectPosition: 'center' }}
        quality={100}
      />
      <div className="absolute bg-white shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-lg">
        <div className="flex flex-col items-center gap-5 h-[60vh] sm:max-h-[60vh]">
          <Image
            className="my-2"
            src="/images/dh_ai_logo.svg"
            alt="Background"
            width={250}
            height={50}
          />
          <h1 className="text-2xl font-bold text-secondary-dark">
            Select Organization
          </h1>
          <p className="text-sm text-slate-600">
            Sign in as an <strong>admin</strong> to any of the following
            organizations
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
                      'w-full cursor-pointer hover:bg-gray-100 px-8 py-4 flex justify-between items-center',
                      isSelected(organization.id)
                        ? 'font-semibold bg-gray-200 hover:bg-gray-200 text-secondary'
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
          <Button
            variant="secondary"
            className="w-full"
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
                Signing In
              </>
            ) : (
              'Sign In'
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default withPageAuthRequired(SelectOrganizationPage)
