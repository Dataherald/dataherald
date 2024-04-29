import BackgroundPageLayout from '@/components/layout/background-page-layout'
import useIsMobile from '@/hooks/ui/useIsMobile'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { Monitor } from 'lucide-react'
import Head from 'next/head'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { FC } from 'react'

const SwitchLargerDevicePage: FC = () => {
  const isMobile = useIsMobile()
  const router = useRouter()

  if (isMobile === false) {
    router.push('/')
  }

  return (
    isMobile && (
      <BackgroundPageLayout>
        <Head>
          <title>Switch to larger screen - Dataherald API</title>
        </Head>
        <div className="bg-white flex flex-col items-center sm:gap-5 shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-lg">
          <Image
            priority
            className="my-2"
            src="/images/dh-logo-color.svg"
            alt="Background"
            width={250}
            height={50}
          />
          <div className="grow flex flex-col items-center justify-center gap-5 sm:max-h-[60vh] text-center">
            <Monitor size={75} strokeWidth={1} className="text-secondary" />
            <h1 className="text-2xl font-semibold text-secondary">
              Best on Larger Screens
            </h1>
            <p className="text-slate-500">
              Our platform is exclusively designed for large screens. Please
              switch to a larger screen device to access it.
            </p>
          </div>
        </div>
      </BackgroundPageLayout>
    )
  )
}

export default withPageAuthRequired(SwitchLargerDevicePage)
