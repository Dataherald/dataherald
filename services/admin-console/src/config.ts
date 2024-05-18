const isServer = typeof window === 'undefined';
export const API_URL = isServer ? process.env.DOCKER_API_URL || process.env.NEXT_PUBLIC_API_URL : process.env.NEXT_PUBLIC_API_URL;
export const AUTH = {
  hostname: process.env.AUTH0_BASE_URL,
  cliendId: process.env.AUTH0_CLIENT_ID,
  domain: process.env.AUTH0_ISSUER_BASE_URL,
  audience: process.env.AUTH0_API_AUDIENCE,
  scope: process.env.AUTH0_SCOPE,
}
export const POSTHOG_DISABLED =
  process.env.NEXT_PUBLIC_POSTHOG_DISABLED === 'true' || false
export const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
export const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST
export const STRIPE_PUBLIC_KEY = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
