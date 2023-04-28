import { handleAuth, handleLogin } from "@auth0/nextjs-auth0";

export default handleAuth({
  signup: handleLogin({ authorizationParams: { screen_hint: "signup" } }),
  onError(req, res, error) {
    console.error(error);
    res.writeHead(302, {
      Location: `/error/auth?message=${encodeURIComponent(error.message)}`,
    });
    res.end();
  },
});
