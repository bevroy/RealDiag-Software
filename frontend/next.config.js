/** @type {import('next').NextConfig} */
const isNetlifyBuild = process.env.NETLIFY === 'true'

const nextConfig = {
  reactStrictMode: true,
  ...(isNetlifyBuild ? { output: 'export' } : {}),
  distDir: 'out',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
