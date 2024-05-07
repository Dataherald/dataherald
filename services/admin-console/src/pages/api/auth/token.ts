import { getAccessToken, withApiAuthRequired } from '@auth0/nextjs-auth0'
import { NextApiRequest, NextApiResponse } from 'next'

export default withApiAuthRequired(
  async (req: NextApiRequest, res: NextApiResponse) => {
    try {
      const { accessToken } = await getAccessToken(req, res)
      res.status(200).json(accessToken)
    } catch (error) {
      console.error('Error fetching access token:', error)

      // Redirect user to logout
      res.writeHead(302, {
        Location: '/api/auth/logout',
      })
      res.end()
    }
  },
)
