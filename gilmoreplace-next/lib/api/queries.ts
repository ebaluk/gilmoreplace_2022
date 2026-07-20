/**
 * TanStack Query `queryOptions` factories for headless API data.
 * `staleTime` is 60s to align with Next fetch `revalidate: 60` / ISR.
 * Keys must match SSR prefetch in `prefetch-page.ts`.
 */

import { queryOptions } from "@tanstack/react-query";
import {
  getAllPages,
  getForm,
  getNavigation,
  getPageBySlug,
  getSettings,
  getThemes,
  getTowerData,
} from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";

const STALE_TIME_MS = 60_000;

/** Page by slug for a Next.js locale segment. */
export function pageBySlugQuery(locale: string, slug: string) {
  return queryOptions({
    queryKey: queryKeys.pages.bySlug(locale, slug),
    queryFn: () => getPageBySlug(slug, locale),
    staleTime: STALE_TIME_MS,
  });
}

/** Navigation tree for a locale. */
export function navigationQuery(locale: string) {
  return queryOptions({
    queryKey: queryKeys.navigation(locale),
    queryFn: () => getNavigation(locale),
    staleTime: STALE_TIME_MS,
  });
}

/** Site + language-root settings. */
export function settingsQuery(locale: string) {
  return queryOptions({
    queryKey: queryKeys.settings(locale),
    queryFn: () => getSettings(locale),
    staleTime: STALE_TIME_MS,
  });
}

/** Full page list under a language root. */
export function allPagesQuery(locale: string) {
  return queryOptions({
    queryKey: queryKeys.pages.all(locale),
    queryFn: () => getAllPages(locale),
    staleTime: STALE_TIME_MS,
  });
}

/** WtForm schema; disabled when `formId <= 0`. */
export function formQuery(formId: number) {
  return queryOptions({
    queryKey: queryKeys.form(formId),
    queryFn: () => getForm(formId),
    staleTime: STALE_TIME_MS,
    enabled: formId > 0,
  });
}

/** CMS CSS themes. */
export function themesQuery() {
  return queryOptions({
    queryKey: queryKeys.themes(),
    queryFn: () => getThemes(),
    staleTime: STALE_TIME_MS,
  });
}

/** Tower bedroom/penthouse types and shared blocks. */
export function towerDataQuery() {
  return queryOptions({
    queryKey: queryKeys.towerData(),
    queryFn: () => getTowerData(),
    staleTime: STALE_TIME_MS,
  });
}
