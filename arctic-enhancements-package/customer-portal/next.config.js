/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: 'https://api.arcticicesolutions.com/v2',
    NEXT_PUBLIC_BASE_URL: 'https://arcticicesolutions.com',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.arcticicesolutions.com/v2/:path*',
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
