import { AUTH0_API_AUDIENCE } from '@/env-variables';
import apiService from '@/services/api';
import {
  HandlerError,
  handleAuth,
  handleCallback,
  handleLogin,
} from '@auth0/nextjs-auth0';
import { AfterCallback } from '@auth0/nextjs-auth0/dist/auth0-session';
import { NextApiRequest, NextApiResponse } from 'next';

const afterCallback: AfterCallback = async (req, res, session) => {
  const { user } = session;
  try {
    await apiService.login(user);
  } catch (e) {
    console.error(e);
  }
  return session;
};

export default handleAuth({
  login: handleLogin({
    authorizationParams: {
      audience: AUTH0_API_AUDIENCE,
    },
  }),
  signup: handleLogin({
    authorizationParams: {
      audience: AUTH0_API_AUDIENCE,
      screen_hint: 'signup',
    },
  }),
  callback: handleCallback({ afterCallback }),
  onError(_: NextApiRequest, res: NextApiResponse, error: HandlerError) {
    console.error(error);
    res.writeHead(302, {
      Location: `/error/auth?message=${encodeURIComponent(error.message)}`,
    });
    res.end();
  },
});
