/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    API_BASE_URL: 'https://api.arcticicesolutions.com',
    NEXT_PUBLIC_API_URL: 'https://api.arcticicesolutions.com',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.arcticicesolutions.com/:path*',
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: 'https://arcticicesolutions.com' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type,Authorization' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
