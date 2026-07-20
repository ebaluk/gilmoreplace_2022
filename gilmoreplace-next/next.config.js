/** @type {import('next').NextConfig} */

const apiUrl = process.env.WAGTAIL_API_URL || "http://localhost:8000/api/v2";
// Derive base URL by stripping /api/v2 suffix
const apiBase = apiUrl.replace(/\/api\/v2\/?$/, "");
const apiHost = new URL(apiBase).hostname;

const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: apiHost,
        port: "8000",
        pathname: "/media_files/**",
      },
    ],
  },
  env: {
    WAGTAIL_API_URL: apiUrl,
    REVALIDATION_SECRET: process.env.REVALIDATION_SECRET || "change-me-in-production",
    NEXT_PUBLIC_GOOGLE_MAPS_KEY: process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || "AIzaSyBT3agucwzH4RQvZ0QQEOCzY44P4t9uAFM",
    NEXT_PUBLIC_RECAPTCHA_SITE_KEY: process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || "6LcTW10UAAAAAODX0vJJkPy7ijRn3LqkE0rvo1FI",
  },
  async redirects() {
    return [
      { source: "/en-us", destination: "/en", permanent: true },
      { source: "/en-us/:path*", destination: "/en/:path*", permanent: true },
      { source: "/zh-hans", destination: "/sc", permanent: true },
      { source: "/zh-hans/:path*", destination: "/sc/:path*", permanent: true },
      { source: "/zh-hant", destination: "/tc", permanent: true },
      { source: "/zh-hant/:path*", destination: "/tc/:path*", permanent: true },
    ];
  },
  async rewrites() {
    const baseUrl = apiBase;
    return [
      {
        source: "/media_files/:path*",
        destination: `${baseUrl}/media_files/:path*`,
      },
      {
        source: "/media/:path*",
        destination: `${baseUrl}/media/:path*`,
      },
      {
        source: "/documents/:path*",
        destination: `${baseUrl}/documents/:path*`,
      },
      {
        source: "/static/:path*",
        destination: "/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
