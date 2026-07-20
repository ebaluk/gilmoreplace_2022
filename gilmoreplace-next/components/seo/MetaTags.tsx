/**
 * SEO MetaTags from page.meta / settings.
 */

import Head from "next/head";
import { type PageMeta, type ImageData } from "@/types/page";

interface MetaTagsProps {
  meta?: PageMeta | null;
  url: string;
  ogImage?: ImageData | null;
  fbAppId?: string | null;
}

/** Emit title/description/OG tags for the current page. */
export function MetaTags({ meta, url, ogImage, fbAppId }: MetaTagsProps) {
  const siteName = meta?.site_name || "Gilmore Place";
  const title = meta?.title || siteName;
  const description = meta?.description || "";
  const keywords = meta?.keywords || "";

  const imageUrl = ogImage?.url
    ? ogImage.url.startsWith("http")
      ? ogImage.url
      : `${process.env.WAGTAIL_API_URL?.replace("/api/v2", "") || ""}${ogImage.url}`
    : undefined;

  return (
    <Head>
      <title>{title}</title>
      {description && <meta name="description" content={description} />}
      {keywords && <meta name="keywords" content={keywords} />}

      <meta property="og:title" content={title} />
      {description && <meta property="og:description" content={description} />}
      <meta property="og:url" content={url} />
      <meta property="og:site_name" content={siteName} />
      {imageUrl && <meta property="og:image" content={imageUrl} />}
      {fbAppId && <meta property="fb:app_id" content={fbAppId} />}

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      {description && <meta name="twitter:description" content={description} />}
      {imageUrl && <meta name="twitter:image" content={imageUrl} />}

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
    </Head>
  );
}
