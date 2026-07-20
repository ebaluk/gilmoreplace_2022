/**
 * URL helpers: Wagtail ↔ Next.js paths, stream-link href resolution.
 */

import { type Locale, locales, defaultLocale } from "@/lib/i18n/config";

const WAGTAIL_PREFIX_TO_LOCALE: Record<string, Locale> = {
  en: "en",
  "en-us": "en",
  sc: "sc",
  tc: "tc",
  "zh-hans": "sc",
  "zh-hant": "tc",
};

function toValidLocale(value: string, fallback: string): string {
  if ((locales as readonly string[]).includes(value)) return value;
  return WAGTAIL_PREFIX_TO_LOCALE[value] || fallback;
}

/** True for `/documents/`, `/media/`, `/media_files/` links (bypass locale mapping). */
export function isDirectAssetLink(href: string): boolean {
  return (
    href.startsWith("/documents/") ||
    href.startsWith("/media/") ||
    href.startsWith("/media_files/")
  );
}

/**
 * Convert a Wagtail absolute path (e.g. `/en/homes/…`) into a Next.js locale path.
 * Asset URLs are returned unchanged.
 */
export function wagtailUrlToNextPath(
  wagtailUrl: string | null | undefined,
  fallbackLocale: string
): string {
  if (!wagtailUrl) return `/${fallbackLocale}`;

  const normalized = wagtailUrl.replace(/\/+$/, "") || "/";
  if (isDirectAssetLink(normalized)) {
    return normalized;
  }
  const parts = normalized.split("/").filter(Boolean);

  if (parts.length === 0) return `/${fallbackLocale}`;

  const nextLocale = toValidLocale(parts[0], fallbackLocale);
  const rest = parts.slice(1).join("/");

  return rest ? `/${nextLocale}/${rest}` : `/${nextLocale}`;
}

/** Whether `currentPath` matches or is under the Wagtail URL mapped for `locale`. */
export function isActivePath(
  wagtailUrl: string,
  currentPath: string,
  locale: string
): boolean {
  const nextPath = wagtailUrlToNextPath(wagtailUrl, locale);
  return (
    currentPath === nextPath ||
    currentPath.startsWith(`${nextPath}/`)
  );
}

/** Value payload for CMS link / email / phone / form stream links. */
export interface StreamLinkValue {
  title?: string;
  link_type?: string;
  link?: string | number;
  new_window?: boolean;
  resolved_link?: { url?: string; id?: number; title?: string; submit_url?: string } | null;
}

/** Resolve a stream-link block to an href (mailto/tel/resolved URL/raw string). */
export function resolveStreamLinkHref(
  linkType: string | undefined,
  value: StreamLinkValue
): string | null {
  const raw = value.link;
  if (linkType === "email_link" && typeof raw === "string") {
    return `mailto:${raw}`;
  }
  if (linkType === "phone_link" && typeof raw === "string") {
    return `tel:${raw}`;
  }
  if (value.resolved_link?.url) {
    return value.resolved_link.url;
  }
  if (typeof raw === "string" && raw) {
    return raw;
  }
  return null;
}

/** External if http(s), mailto, tel, or a direct asset path. */
export function isExternalStreamLink(href: string): boolean {
  return (
    href.startsWith("http") ||
    href.startsWith("mailto:") ||
    href.startsWith("tel:") ||
    isDirectAssetLink(href)
  );
}
