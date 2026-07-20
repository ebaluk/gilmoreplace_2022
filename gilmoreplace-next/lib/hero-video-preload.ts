/**
 * Warm hero MP4/poster via link preload + optional hidden video element.
 */

import { type QueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/api/query-keys";
import { pageBySlugQuery } from "@/lib/api/queries";
import { locales, type Locale } from "@/lib/i18n/config";
import { pickHeroMp4Url, pickHeroPosterUrl } from "@/lib/hero-video";
import type { WagtailPage } from "@/types/page";

const preloadedHrefs = new Set<string>();
let warmVideoEl: HTMLVideoElement | null = null;
let warmVideoSrc: string | null = null;

/** Parse `/locale/...slug` from pathname; null if locale invalid. */
export function localeAndSlugFromPathname(
  pathname: string,
): { locale: Locale; slug: string } | null {
  const segments = pathname.split("/").filter(Boolean);
  const locale = segments[0];
  if (!locale || !locales.includes(locale as Locale)) return null;
  const slug = segments.slice(1).join("/");
  return { locale: locale as Locale, slug };
}

function injectLinkPreload(
  href: string,
  as: string,
  extra?: Record<string, string>,
): void {
  if (typeof document === "undefined" || !href || preloadedHrefs.has(href)) return;
  preloadedHrefs.add(href);

  const selector = `link[rel="preload"][href="${CSS.escape(href)}"]`;
  if (document.head.querySelector(selector)) return;

  const link = document.createElement("link");
  link.rel = "preload";
  link.href = href;
  link.as = as;
  if (extra) {
    for (const [key, value] of Object.entries(extra)) {
      link.setAttribute(key, value);
    }
  }
  document.head.appendChild(link);
}

function warmVideoInBackground(mp4Url: string): void {
  if (typeof document === "undefined" || !mp4Url) return;
  if (warmVideoSrc === mp4Url && warmVideoEl) return;

  if (!warmVideoEl) {
    warmVideoEl = document.createElement("video");
    warmVideoEl.muted = true;
    warmVideoEl.playsInline = true;
    warmVideoEl.preload = "auto";
    warmVideoEl.setAttribute("aria-hidden", "true");
    warmVideoEl.tabIndex = -1;
    warmVideoEl.style.cssText =
      "position:absolute;width:0;height:0;opacity:0;pointer-events:none";
    document.body.appendChild(warmVideoEl);
  }

  if (warmVideoSrc !== mp4Url) {
    warmVideoSrc = mp4Url;
    warmVideoEl.src = mp4Url;
    warmVideoEl.load();
  }
}

/** Inject preload links and warm a hidden video element for mp4/poster. */
export function preloadHeroVideoAssets(
  mp4Url?: string,
  posterUrl?: string,
): void {
  if (posterUrl) {
    injectLinkPreload(posterUrl, "image", { fetchpriority: "high" });
  }
  if (mp4Url) {
    injectLinkPreload(mp4Url, "video", { type: "video/mp4" });
    warmVideoInBackground(mp4Url);
  }
}

function preloadHeroFromPage(page: WagtailPage | undefined): void {
  if (!page?.hero?.video?.transcodes?.length) return;
  preloadHeroVideoAssets(
    pickHeroMp4Url(page.hero.video),
    pickHeroPosterUrl(page.hero.video, page.hero.images),
  );
}

/** Fetch/cached page by slug and preload its hero media. */
export function preloadHeroForSlug(
  queryClient: QueryClient,
  locale: Locale,
  slug: string,
): void {
  const cached = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(locale, slug),
  );
  if (cached) {
    preloadHeroFromPage(cached);
    return;
  }

  void queryClient.fetchQuery(pageBySlugQuery(locale, slug)).then(preloadHeroFromPage);
}

/** Parse locale/slug from pathname and preload that page's hero. */
export function preloadHeroForPathname(
  queryClient: QueryClient,
  pathname: string,
): void {
  const parsed = localeAndSlugFromPathname(pathname);
  if (!parsed) return;

  const { locale, slug } = parsed;
  preloadHeroForSlug(queryClient, locale, slug);

  // Logo often returns home — keep homepage video warm while browsing inside the site.
  if (slug !== "") {
    preloadHeroForSlug(queryClient, locale, "");
  }
}

/** Warm homepage hero from an already-hydrated QueryClient cache. */
export function preloadHomepageHeroFromCache(
  queryClient: QueryClient,
  locale: Locale,
): void {
  preloadHeroForSlug(queryClient, locale, "");
}
