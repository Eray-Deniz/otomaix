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
  // Source map yükleme devre dışı (Coolify build — SENTRY_AUTH_TOKEN gerekmez)
  silent: true,
  disableLogger: true,
  hideSourceMaps: true,
  // Sentry DSN yoksa Sentry devre dışı
  autoInstrumentServerFunctions: true,
  autoInstrumentAppDirectory: true,
})
