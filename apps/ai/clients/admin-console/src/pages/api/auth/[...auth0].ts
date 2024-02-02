import { API_URL, AUTH } from '@/config'
import { serverFetcher } from '@/lib/api/server-fetcher'
import { User } from '@/models/api'
import {
  AfterCallback,
  HandlerError,
  Session,
  handleAuth,
  handleCallback,
  handleLogin,
} from '@auth0/nextjs-auth0'
import { NextApiRequest, NextApiResponse } from 'next'

/**
 * The signup and login will be handled by auth0. We would have to deal with both in the backend and do each flow depending on if the user exists or not.
 */
const afterCallback: AfterCallback = async (
  req: NextApiRequest,
  res: NextApiResponse,
  session: Session,
) => {
  const { user: auth0User, accessToken: token } = session
  try {
    const user: User = await serverFetcher<User>(`${API_URL}/auth/login`, {
      body: JSON.stringify(auth0User),
      method: 'POST',
      token,
    })
    const sessionUser: User = {
      ...auth0User,
      ...user,
    }
    session.user = sessionUser
  } catch (e: unknown) {
    const error = e as Error
    console.error(error)
    res.writeHead(302, {
      Location: `/auth/error?message=${encodeURIComponent(e as string)}`,
    })
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
