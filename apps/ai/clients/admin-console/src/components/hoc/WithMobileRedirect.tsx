import useIsMobile from '@/hooks/ui/useIsMobile'
import { useRouter } from 'next/navigation'
import { FC, ReactNode, useEffect } from 'react'

interface WithMobileRedirectProps {
  children: ReactNode
}

const WithMobileRedirect: FC<WithMobileRedirectProps> = ({ children }) => {
  const isMobile = useIsMobile()
  const router = useRouter()

  useEffect(() => {
    if (isMobile) {
      router.push('/switch-to-larger-screen')
    }
  }, [isMobile, router])

  return <>{children}</>
}

export default WithMobileRedirect
