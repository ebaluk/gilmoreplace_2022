/**
 * SEO helpers for App Router `generateMetadata` + optional JSON-LD in the page body.
 */

import type { Metadata } from "next";
import { type PageMeta, type ImageData } from "@/types/page";

function absoluteImageUrl(ogImage?: ImageData | null): string | undefined {
  if (!ogImage?.url) return undefined;
  if (ogImage.url.startsWith("http")) return ogImage.url;
  const origin =
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.WAGTAIL_API_URL?.replace(/\/api\/v2\/?$/, "") ||
    "";
  return `${origin.replace(/\/$/, "")}${ogImage.url}`;
}

/** Build Next.js Metadata from Wagtail page.meta. */
export function buildPageMetadata(opts: {
  meta?: PageMeta | null;
  url: string;
  ogImage?: ImageData | null;
  fbAppId?: string | null;
}): Metadata {
  const siteName = opts.meta?.site_name || "Gilmore Place";
  const title = opts.meta?.title || siteName;
  const description = opts.meta?.description || "";
  const keywords = opts.meta?.keywords || "";
  const imageUrl = absoluteImageUrl(opts.ogImage ?? opts.meta?.og_image);

  return {
    title,
    description: description || undefined,
    keywords: keywords || undefined,
    openGraph: {
      title,
      description: description || undefined,
      url: opts.url,
      siteName,
      images: imageUrl ? [{ url: imageUrl }] : undefined,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: description || undefined,
      images: imageUrl ? [imageUrl] : undefined,
    },
    other: opts.fbAppId ? { "fb:app_id": opts.fbAppId } : undefined,
  };
}

/** JSON-LD WebPage snippet for the document body. */
export function PageJsonLd({
  meta,
  url,
  ogImage,
}: {
  meta?: PageMeta | null;
  url: string;
  ogImage?: ImageData | null;
}) {
  const siteName = meta?.site_name || "Gilmore Place";
  const title = meta?.title || siteName;
  const description = meta?.description || "";
  const imageUrl = absoluteImageUrl(ogImage ?? meta?.og_image);

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebPage",
          name: title,
          description,
          url,
          ...(imageUrl ? { image: imageUrl } : {}),
        }),
      }}
    />
  );
}
