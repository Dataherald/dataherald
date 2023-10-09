export const API_URL = process.env.NEXT_PUBLIC_API_URL
export const AUTH = {
  hostname: process.env.AUTH0_BASE_URL,
  cliendId: process.env.AUTH0_CLIENT_ID,
  domain: process.env.AUTH0_ISSUER_BASE_URL,
  audience: process.env.AUTH0_API_AUDIENCE,
  scope: process.env.AUTH0_SCOPE,
}
export const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
export const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST
