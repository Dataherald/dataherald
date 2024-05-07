import { UserProvider, useUser } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/navigation'
import React, {
  ComponentType,
  FC,
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react'

interface AuthProviderProps {
  children: ReactNode
}

type WithAuthUser = (
  Component: ComponentType<AuthProviderProps>,
) => React.FC<AuthProviderProps>

const withAuthUser: WithAuthUser = (Component) => {
  return function WithAuthUser(props: AuthProviderProps): JSX.Element {
    return (
      <UserProvider>
        <Component {...props} />
      </UserProvider>
    )
  }
}

interface AuthContextType {
  token: string | null
  fetchToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: FC<AuthProviderProps> = withAuthUser(
  ({ children }) => {
    const router = useRouter()
    const { user: sessionUser } = useUser()
    const [token, setToken] = useState<string | null>(null)

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
      !!sessionUser && fetchToken()
    }, [fetchToken, sessionUser])

    return (
      <AuthContext.Provider value={{ token, fetchToken }}>
        {children}
      </AuthContext.Provider>
    )
  },
)

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
