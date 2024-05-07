let cachedToken = null
let expiryTime = null

async function getApiAuthToken() {
    if (cachedToken && expiryTime && new Date().getTime() < expiryTime) {
        return cachedToken
    }

    const body = {
        client_id: process.env.AUTH0_CLIENT_ID,
        client_secret: process.env.AUTH0_CLIENT_SECRET,
        audience: process.env.AUTH0_API_AUDIENCE,
        grant_type: 'client_credentials',
    }

    try {
        const response = await fetch(
            `https://${process.env.AUTH0_DOMAIN}/oauth/token`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            }
        )

        const data = await response.json()

        cachedToken = data.access_token
        expiryTime = new Date().getTime() + data.expires_in * 1000

        return cachedToken
    } catch (error) {
        console.error('Error getting Auth0 token:', error)
        throw error
    }
}

module.exports = getApiAuthToken
