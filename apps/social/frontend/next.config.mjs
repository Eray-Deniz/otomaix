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
      // fal.ai temp storage — Nano Banana / FLUX still URL'leri (24h TTL).
      // Geçici fallback: backend thumbnail_url henüz set edilmediği post'larda
      // template_fields.still_image_url fal.media URL'i ile gösterilebilsin.
      {
        protocol: 'https',
        hostname: 'v3b.fal.media',
      },
      {
        protocol: 'https',
        hostname: 'v3.fal.media',
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
