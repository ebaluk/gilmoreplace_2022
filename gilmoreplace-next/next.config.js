/** @type {import('next').NextConfig} */

const apiUrl = process.env.WAGTAIL_API_URL || "http://localhost:8000/api/v2";
// Derive base URL by stripping /api/v2 suffix
const apiBase = apiUrl.replace(/\/api\/v2\/?$/, "");
let apiHost = "localhost";
try {
  apiHost = new URL(apiBase).hostname;
} catch {
  // keep localhost
}

const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: apiHost,
        pathname: "/media_files/**",
      },
      {
        protocol: "https",
        hostname: apiHost,
        pathname: "/media_files/**",
      },
    ],
  },
  // Do NOT put secrets in `env` — that inlines them into the client bundle.
  // Server code reads process.env.REVALIDATION_SECRET / PREVIEW_SECRET / WAGTAIL_API_URL at runtime.
  // Browser-only values must use NEXT_PUBLIC_* (set in the environment, not hardcoded here).
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
