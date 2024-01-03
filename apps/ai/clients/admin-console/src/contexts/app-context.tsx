import { useGetOrganization } from '@/hooks/api/organization/useGetOrganization'
import { useGetUser } from '@/hooks/api/user/useGetUser'
import { usePatchUser } from '@/hooks/api/user/usePatchUser'
import { Organization, User } from '@/models/api'
import { useUser } from '@auth0/nextjs-auth0/client'
import { useRouter } from 'next/router'
import {
  FC,
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useReducer,
} from 'react'

interface AppState {
  user: User | null
  organization: Organization | null
}

interface AppContextType extends AppState {
  logout: () => void
  updateOrganization: () => Promise<void>
  setAdminOrganization: (organizationId: string) => Promise<void>
}

const AppContext = createContext<AppContextType | undefined>(undefined)

interface AppContextTypeProps {
  children: ReactNode
}

const initialState: AppState = {
  user: null,
  organization: null,
}

type Action =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ORG'; payload: Organization | null }
  | { type: 'LOGOUT' }

const reducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'SET_ORG':
      return { ...state, organization: action.payload }
    case 'LOGOUT':
      return { ...initialState }
    default:
      throw new Error(`Unhandled action type: ${action}`)
  }
}

export const AppContextProvider: FC<AppContextTypeProps> = ({ children }) => {
  const router = useRouter()
  const { user: sessionUser, isLoading: isLoadingSession } = useUser()
  const [state, dispatch] = useReducer(reducer, initialState)

  const getOrganization = useGetOrganization()
  const patchUserApi = usePatchUser()
  const getUserApi = useGetUser()

  const fetchOrganization = useCallback(
    async (organizationId: string): Promise<Organization> => {
      try {
        return getOrganization(organizationId)
      } catch (error) {
        console.error(`Fetching organization failed: ${error}`)
        throw error
      }
    },
    [getOrganization],
  )

  const fetchUser = useCallback(
    async (userId: string): Promise<User> => {
      try {
        return getUserApi(userId)
      } catch (error) {
        console.error(`Fetching User failed: ${error}`)
        throw error
      }
    },
    [getUserApi],
  )

  const patchUser = useCallback(
    async (userUpdates: User): Promise<User> => {
      const currentUser = state.user
      if (!currentUser) throw new Error('No user found in app state')
      try {
        const updatedUser = await patchUserApi(currentUser.id, userUpdates)
        return updatedUser
      } catch (error) {
        console.error(`Error patching user: ${error}`)
        throw error
      }
    },
    [patchUserApi, state.user],
  )

  const setAdminOrganization = useCallback(
    async (organizationId: string): Promise<void> => {
      const updateAdmin = async (organizationId: string) => {
        try {
          const updatedUser = await patchUser({
            ...(state.user as User),
            organization_id: organizationId,
          })
          try {
            const organization = await fetchOrganization(
              updatedUser.organization_id,
            )
            dispatch({ type: 'SET_ORG', payload: organization })
            dispatch({
              type: 'SET_USER',
              payload: updatedUser,
            })
          } catch (error) {
            console.error(`Fetching organization failed: ${error}`)
            throw error
          }
        } catch (error) {
          console.error(`Error patching user: ${error}`)
        }
      }

      if (organizationId) {
        return updateAdmin(organizationId)
      }
    },
    [fetchOrganization, patchUser, state.user],
  )

  const updateOrganization = useCallback(async () => {
    if (!state.organization) return
    const organization = await fetchOrganization(state.organization.id)
    dispatch({ type: 'SET_ORG', payload: organization })
  }, [fetchOrganization, state.organization])

  const logout = useCallback(async () => {
    await router.push('/api/auth/logout')
    dispatch({ type: 'LOGOUT' })
  }, [router])

  useEffect(() => {
    if (state.user) return // user already set
    if (isLoadingSession || !sessionUser) return // not authenticated user

    const getUser = async (userId: string) => {
      try {
        const user = await fetchUser(userId)
        dispatch({ type: 'SET_USER', payload: user })
      } catch (error) {
        console.error(`Fetching User failed: ${error}`)
      }
    }
    getUser((sessionUser as User).id)
  }, [fetchUser, isLoadingSession, sessionUser, state.user])

  // Fetch current user organization
  useEffect(() => {
    if (state.organization || !state.user) return // no user or org already set

    const fetchOrg = async (organizationId: string) => {
      try {
        const organization = await fetchOrganization(organizationId)
        dispatch({ type: 'SET_ORG', payload: organization })
      } catch (error) {
        console.error(`Fetching organization failed: ${error}`)
      }
    }
    fetchOrg(state.user.organization_id)
  }, [fetchOrganization, state.organization, state.user])

  return (
    <AppContext.Provider
      value={{
        ...state,
        setAdminOrganization,
        updateOrganization,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within an AppContextProvider')
  }
  return context
}
