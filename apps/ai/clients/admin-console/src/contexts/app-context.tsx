import LoadingPage from '@/components/layout/loading-page'
import { useGetOrganization } from '@/hooks/api/organization/useGetOrganization'
import { useGetUser } from '@/hooks/api/user/useGetUser'
import { usePatchUser } from '@/hooks/api/user/usePatchUser'
import { ERole, Organization, User } from '@/models/api'
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

const ADMIN_SELECTED_ORG_KEY = 'adminSelectedOrg'

interface AppState {
  loadingUser: boolean
  selectingOrg: boolean
  user: User | null
  organization: Organization | null
}

interface AppContextType extends AppState {
  logout: () => void
  setAdminOrganization: (organizationId: string | null) => Promise<void>
}

const AppContext = createContext<AppContextType | undefined>(undefined)

interface AppContextTypeProps {
  children: ReactNode
}

const initialState: AppState = {
  loadingUser: false,
  selectingOrg: false,
  user: null,
  organization: null,
}

type Action =
  | { type: 'SET_LOADING_USER'; payload: boolean }
  | { type: 'SET_SELECTING_ORG'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ORG'; payload: Organization | null }
  | { type: 'LOGOUT' }

const reducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'SET_LOADING_USER':
      return { ...state, loadingUser: action.payload }
    case 'SET_SELECTING_ORG':
      return { ...state, selectingOrg: action.payload }
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
    async (userUpdates: Partial<User>): Promise<User> => {
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
    async (organizationId: string | null): Promise<void> => {
      const updateAdmin = async (organizationId: string) => {
        try {
          const updatedUser = await patchUser({
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
            dispatch({ type: 'SET_SELECTING_ORG', payload: false })
            localStorage.setItem(ADMIN_SELECTED_ORG_KEY, 'true')
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
      } else {
        return new Promise((resolve) =>
          resolve(localStorage.removeItem(ADMIN_SELECTED_ORG_KEY)),
        )
      }
    },
    [fetchOrganization, patchUser],
  )

  const logout = useCallback(async () => {
    await setAdminOrganization(null)
    dispatch({ type: 'LOGOUT' })
    router.push('/api/auth/logout')
  }, [router, setAdminOrganization])

  // Handle setting app user from session and start loading user data
  useEffect(() => {
    if (state.user) return // user already set
    if (isLoadingSession) {
      dispatch({ type: 'SET_LOADING_USER', payload: true })
      return
    }
    if (!sessionUser) {
      // not authenticated user
      dispatch({ type: 'SET_LOADING_USER', payload: false })
      return
    }
    const getUser = async (userId: string) => {
      try {
        const user = await fetchUser(userId)
        dispatch({ type: 'SET_USER', payload: user })
      } catch (error) {
        console.error(`Fetching User failed: ${error}`)
      }
    }
    getUser((sessionUser as any)._id)
  }, [fetchUser, isLoadingSession, sessionUser, state.user])

  // Check if app user is admin when loading data
  useEffect(() => {
    if (!state.user || !state.loadingUser || state.selectingOrg) return

    const navigateToSelectOrg = async () => {
      // navigate to select org page and stop loading user data
      dispatch({ type: 'SET_SELECTING_ORG', payload: true })
      await router.push('/select-organization')
      dispatch({ type: 'SET_LOADING_USER', payload: false })
    }

    const isAdmin = state.user.role === ERole.ADMIN
    const adminSelectedOrg =
      localStorage.getItem(ADMIN_SELECTED_ORG_KEY) === 'true'
    if (isAdmin && !adminSelectedOrg) {
      navigateToSelectOrg()
    } else {
      // regular user or admin with selected org
      dispatch({ type: 'SET_LOADING_USER', payload: false })
    }
  }, [router, state.loadingUser, state.selectingOrg, state.user])

  // Fetch current user organization
  useEffect(() => {
    if (
      state.loadingUser ||
      state.selectingOrg ||
      state.organization ||
      !state.user
    ) {
      return
    }
    const fetchOrg = async (organizationId: string) => {
      try {
        const organization = await fetchOrganization(organizationId)
        dispatch({ type: 'SET_ORG', payload: organization })
      } catch (error) {
        console.error(`Fetching organization failed: ${error}`)
      }
    }
    fetchOrg(state.user.organization_id)
  }, [
    fetchOrganization,
    state.loadingUser,
    state.organization,
    state.selectingOrg,
    state.user,
  ])

  return (
    <AppContext.Provider
      value={{
        ...state,
        setAdminOrganization,
        logout,
      }}
    >
      {state.loadingUser ? <LoadingPage /> : children}
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
