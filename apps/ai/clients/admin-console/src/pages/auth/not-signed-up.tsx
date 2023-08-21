import { Button } from '@/components/ui/button'
import { AUTH } from '@/config'
import { UserCog2 } from 'lucide-react'
import { GetServerSideProps } from 'next'
import Image from 'next/image'
import { FC } from 'react'

export const getServerSideProps: GetServerSideProps = async () => {
  const logoutUrl = `${AUTH.domain}/v2/logout?client_id=${AUTH.cliendId}&returnTo=${AUTH.hostname}`

  return {
    props: {
      logoutUrl,
    },
  }
}

const AuthErrorPage: FC<{
  logoutUrl: string
}> = ({ logoutUrl }) => {
  const logoutUser = async () => {
    window.location.href = logoutUrl
  }

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
        <h1 className="text-xl font-bold mb-4 text-secondary-dark flex items-center gap-3">
          <UserCog2 size={50} />
          Almost there!
        </h1>
        <div className="mb-8">
          <div className="flex flex-col gap-2">
            <p className="text-gray-800 break-words">
              Please, get in touch with us so we can finish the your sign up
              process
            </p>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 justify-end">
          <Button variant="secondary-outline" size="lg" onClick={logoutUser}>
            Try Again
          </Button>
          <Button variant="secondary" size="lg">
            <a href="mailto:support@dataherald.com">Contact us</a>{' '}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default AuthErrorPage
