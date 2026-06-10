/** @type {import('next').NextConfig} */

// Determine base path from environment or default to /Jimmy for GitHub Pages
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '/Jimmy';

// API base URL - Production uses Render backend, dev uses localhost
const isProduction = process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_API_BASE;
const apiBase = process.env.NEXT_PUBLIC_API_BASE 
  ? (process.env.NEXT_PUBLIC_API_BASE).replace(/\/$/, '')
  : isProduction 
    ? 'https://jimmy-ai-bot.onrender.com'
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
};

module.exports = nextConfig;
