/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/',
        destination: '/queries',
        permanent: true,
      },
    ]
  },
}

module.exports = nextConfig
