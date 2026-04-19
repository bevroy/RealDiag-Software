/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // output: 'export',  // Disabled for dev server - enable for static export
  distDir: 'out',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
