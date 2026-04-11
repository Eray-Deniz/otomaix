import { withSentryConfig } from '@sentry/nextjs'

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'pub-a4f7a6ed6ca347f59420695c5b79daaa.r2.dev',
      },
      {
        protocol: 'https',
        hostname: 'assets.otomaix.com',
      },
    ],
  },
}

export default withSentryConfig(nextConfig, {
  silent: true,
  disableLogger: true,
  hideSourceMaps: true,
  autoInstrumentServerFunctions: true,
  autoInstrumentAppDirectory: true,
  sourcemaps: {
    // Build sonrası source map dosyalarını sil — kullanıcıya servis edilmez
    deleteSourcemapsAfterUpload: true,
    disable: true, // SENTRY_AUTH_TOKEN olmadığı için upload'u tamamen devre dışı bırak
  },
})
