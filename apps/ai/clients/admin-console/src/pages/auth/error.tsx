import BackgroundPageLayout from '@/components/layout/background-page-layout'
import { Button } from '@/components/ui/button'
import { AUTH } from '@/config'
import { MailWarning } from 'lucide-react'
import { GetServerSideProps } from 'next'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { FC, useState } from 'react'

enum ERROR_CODES {
  EMAIL_NOT_VERIFIED = 'Email Not Verified',
}

/**
 * Auth0 wraps several errors like unverified emails into a CallbackError
 * We implemented this to catch different callback scenarios and catch the errors for UX
 * @param errorDescription
 * @returns
 */
const getErrorCause = (errorDescription: string): string => {
  const error = (errorDescription.match(/---(.*?)\)/) || '')[1]
  switch (error) {
    case ERROR_CODES.EMAIL_NOT_VERIFIED:
      return 'Verify your email address'
    default:
      return "We couldn't verify your identity"
  }
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { message = '' } = context.query
  const errorDescription = message as string
  const isEmailNotVerified = errorDescription?.includes(
    ERROR_CODES.EMAIL_NOT_VERIFIED,
  )
  const errorCause = getErrorCause(errorDescription)

  const logoutUrl = `${AUTH.domain}/v2/logout?client_id=${AUTH.cliendId}&returnTo=${AUTH.hostname}`

  return {
    props: {
      errorCause,
      errorDescription,
      isEmailNotVerified,
      logoutUrl,
    },
  }
}

const AuthErrorPage: FC<{
  errorCause: string
  errorDescription: string
  isEmailNotVerified: boolean
  logoutUrl: string
}> = ({ errorCause, errorDescription, isEmailNotVerified, logoutUrl }) => {
  const router = useRouter()
  const [showDetails, setShowDetails] = useState(false)

  const toggleDetails = () => {
    setShowDetails(!showDetails)
  }

  const continueToLogin = async () => {
    router.push('/')
  }

  const logoutUser = async () => {
    window.location.href = logoutUrl
  }

  return (
    <BackgroundPageLayout>
      <Head>
        <title>Authentication error - Dataherald API</title>
      </Head>
      <div className="bg-white shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-lg">
        <h1 className="text-xl font-bold mb-4 text-secondary-dark flex items-center gap-3">
          {isEmailNotVerified && <MailWarning size={50} />}
          {errorCause}
        </h1>
        <div className="mb-8">
          {isEmailNotVerified ? (
            <div className="flex flex-col gap-4">
              <p className="text-slate-800 break-words">
                Check your inbox for the verification email and follow the
                instructions to complete the process.
              </p>
              <p className="text-slate-800 break-words">
                {`If you can't find the email `}
                <a
                  className="text-primary font-semibold hover:underline"
                  href="mailto:support@dataherald.com"
                >
                  contact us
                </a>{' '}
                for assistance.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <p className="text-slate-800 break-words">
                Something went wrong. Please try to log in again by clicking the
                button below or{' '}
                <a
                  className="text-primary font-semibold hover:underline"
                  href="mailto:support@dataherald.com"
                >
                  contact us
                </a>{' '}
                if the issue persists.
              </p>
              {errorDescription && (
                <Button
                  variant="link"
                  className="w-fit p-0 text-primary font-semibold cursor-pointer"
                  onClick={toggleDetails}
                >
                  {showDetails ? 'Hide details' : 'Show details'}
                </Button>
              )}
              {showDetails && (
                <p className="text-slate-500 whitespace-pre-wrap">
                  {errorDescription}
                </p>
              )}
            </div>
          )}
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          {isEmailNotVerified && (
            <button
              className="bg-secondary text-white font-semibold py-2 px-4 rounded-lg w-full"
              onClick={continueToLogin}
            >
              Continue
            </button>
          )}
          {isEmailNotVerified ? (
            <button
              className="bg-white text-secondary border border-secondary font-semibold py-2 px-4 rounded-lg w-full"
              onClick={logoutUser}
            >
              Logout
            </button>
          ) : (
            <button
              className="bg-secondary text-white font-semibold py-2 px-4 rounded-lg w-full"
              onClick={logoutUser}
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </BackgroundPageLayout>
  )
}

export default AuthErrorPage
