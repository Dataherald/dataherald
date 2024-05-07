import { useEffect, useState } from 'react'

const MOBILE_BREAKPOINT = 768

const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState<boolean | null>(null)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT)
    }

    window.addEventListener('resize', handleResize)

    handleResize()

    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return isMobile
}

export default useIsMobile
