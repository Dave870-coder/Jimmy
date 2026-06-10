/** @type {import('next').NextConfig} */

// Detect if building for GitHub Pages specifically
// Set GITHUB_PAGES_BUILD=true to build for GitHub Pages, otherwise use root path
const buildForGitHubPages = process.env.GITHUB_PAGES_BUILD === 'true';

// Determine base path: /Jimmy only for GitHub Pages, empty for everything else
const basePath = buildForGitHubPages ? '/Jimmy' : '';

// API base URL - Production uses Render backend, dev uses localhost
const isProduction = process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_API_BASE;
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
