import { useUser } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/navigation'
import {
  FC,
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react'

interface AuthContextType {
  token: string | null
  fetchToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)
  const { user } = useUser()

  const fetchToken = useCallback(async () => {
    try {
      const response = await fetch('/api/auth/token')
      const token: string = await response.json()
      setToken(token)
    } catch (error) {
      console.error(`Fetching token failed, redirecting to logout: ${error}`)
      router.push('/api/auth/logout')
    }
  }, [router])

  useEffect(() => {
    !!user && fetchToken()
  }, [user, fetchToken])

  return (
    <AuthContext.Provider value={{ token, fetchToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
