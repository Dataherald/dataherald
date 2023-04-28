import { HandlerError, handleAuth, handleLogin } from "@auth0/nextjs-auth0";
import { NextApiRequest, NextApiResponse } from "next";

export default handleAuth({
  signup: handleLogin({ authorizationParams: { screen_hint: "signup" } }),
  onError(req: NextApiRequest, res: NextApiResponse, error: HandlerError) {
    console.error(error);
    res.writeHead(302, {
      Location: `/error/auth?message=${encodeURIComponent(error.message)}`,
    });
    res.end();
  },
});
