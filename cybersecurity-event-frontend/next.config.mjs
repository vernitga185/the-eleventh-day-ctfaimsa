/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/eleventh/:path*',
        destination: 'https://backend-the-eleventh-day-ctfaimsa.onrender.com/api/eleventh/:path*',
      },
      {
        source: '/api/satyajit/:path*',
        destination: 'https://satyajit-of-panchala.onrender.com/api/satyajit/:path*',
      },
    ]
  },
}

export default nextConfig
