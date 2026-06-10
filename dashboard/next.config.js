/** @type {import('next').NextConfig} */

// Determine base path from environment or default to /Jimmy for GitHub Pages
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '/Jimmy';

// API base URL configuration
const apiBase = process.env.NEXT_PUBLIC_API_BASE 
  ? (process.env.NEXT_PUBLIC_API_BASE).replace(/\/$/, '')
  : 'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  distDir: 'out',
  trailingSlash: true,
  basePath: basePath,
  assetPrefix: basePath,
  experimental: {
    typedRoutes: true,
  },
  images: {
    unoptimized: true,
  },
  // Environment variables for client-side
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
    NEXT_PUBLIC_API_BASE: apiBase,
  },
  // Redirect API calls to backend
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/api/:path*',
          destination: `${apiBase}/api/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
