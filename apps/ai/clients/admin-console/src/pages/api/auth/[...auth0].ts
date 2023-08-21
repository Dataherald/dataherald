import { API_URL, AUTH } from '@/config'
import { apiFetcher } from '@/lib/api/fetcher'
import { AuthUser, User } from '@/models/api'
import {
  AfterCallback,
  HandlerError,
  Session,
  handleAuth,
  handleCallback,
  handleLogin,
} from '@auth0/nextjs-auth0'
import { NextApiRequest, NextApiResponse } from 'next'

const afterCallback: AfterCallback = async (
  req: NextApiRequest,
  res: NextApiResponse,
  session: Session,
) => {
  const { user: auth0User, accessToken: token } = session
  try {
    const authUser: AuthUser = await apiFetcher<AuthUser>(
      `${API_URL}/auth/login`,
      {
        body: JSON.stringify(auth0User),
        method: 'POST',
        token,
      },
    )
    const { organization_name, ...userProps } = authUser
    const sessionUser: User = {
      ...auth0User,
      ...userProps,
      // TODO login endpoint should send the full organization
      // Even better, we should fetch user data and login shouldn't return anything
      organization: {
        id: 'unknown',
        name: organization_name,
        slack_workspace_id: 'unknown',
      },
    }
    session.user = sessionUser
  } catch (e: unknown) {
    const error = e as Error
    console.error(error)
    if (error.cause === 401) {
      res.writeHead(302, {
        Location: `/auth/not-signed-up`,
      })
    } else {
      res.writeHead(302, {
        Location: `/auth/error?message=${encodeURIComponent(e as string)}`,
      })
    }
    res.end()
  }
  return session
}

export default handleAuth({
  login: handleLogin({
    authorizationParams: {
      scope: AUTH.scope,
      audience: AUTH.audience,
    },
  }),
  signup: handleLogin({
    authorizationParams: {
      scope: AUTH.scope,
      audience: AUTH.audience,
      screen_hint: 'signup',
    },
  }),
  callback: handleCallback({ afterCallback }),
  onError(_: NextApiRequest, res: NextApiResponse, error: HandlerError) {
    console.error(error)
    res.writeHead(302, {
      Location: `/auth/error?message=${encodeURIComponent(error.message)}`,
    })
    res.end()
  },
})
