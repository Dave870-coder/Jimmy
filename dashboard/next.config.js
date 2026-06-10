/** @type {import('next').NextConfig} */

// Detect if running on Render (production)
const isRender = process.env.PUBLIC_BASE_URL && process.env.PUBLIC_BASE_URL.includes('onrender.com');

// Determine base path: empty for Render/production, /Jimmy for GitHub Pages
const basePath = isRender ? '' : (process.env.NEXT_PUBLIC_BASE_PATH || '/Jimmy');

// API base URL - Production uses Render backend, dev uses localhost
const isProduction = isRender || process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_API_BASE;
const apiBase = process.env.NEXT_PUBLIC_API_BASE 
  ? (process.env.NEXT_PUBLIC_API_BASE).replace(/\/$/, '')
  : isProduction 
    ? (process.env.PUBLIC_BASE_URL || 'https://jimmy-ai-bot.onrender.com')
    : 'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  distDir: 'out',
  trailingSlash: true,
  basePath: basePath,
  assetPrefix: basePath || undefined,
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
