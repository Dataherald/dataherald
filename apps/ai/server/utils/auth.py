import jwt

from config import auth_settings


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{auth_settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # return mock authentication data
        if not auth_settings.auth_enabled:
            return {
                "iss": auth_settings.auth0_issuer,
                "sub": "foo",
                "aud": auth_settings.auth0_audience,
                "iat": "",
                "exp": "",
                "azp": "",
                "scope": "",
                "gty": "client-credentials",
            }
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}
        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=auth_settings.auth0_algorithms,
                audience=auth_settings.auth0_audience,
                issuer=auth_settings.auth0_issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return payload
