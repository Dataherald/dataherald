/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
      {
        protocol: 'https',
        hostname: 's.gravatar.com',
      },
    ],
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/databases',
        permanent: true,
      },
    ]
  },
}

module.exports = nextConfig
