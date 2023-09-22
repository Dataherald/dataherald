import { apiFetcher } from '@/lib/api/fetcher'
import { useUser } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/navigation'
import {
  Dispatch,
  FC,
  ReactNode,
  SetStateAction,
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

interface AuthContextType {
  token: string | null
  setToken: Dispatch<SetStateAction<string | null>>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)
  const { user } = useUser()

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const token: string = await apiFetcher<string>('/api/auth/token')
        setToken(token)
      } catch (error) {
        router.push('/api/auth/login')
      }
    }
    !!user && fetchToken()
  }, [user, router])

  return (
    <AuthContext.Provider value={{ token, setToken }}>
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
