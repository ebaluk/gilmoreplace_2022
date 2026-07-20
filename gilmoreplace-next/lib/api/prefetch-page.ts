/**
 * Server-side TanStack Query prefetch helpers for App Router pages.
 */

import type { QueryClient } from "@tanstack/react-query";
import {
  navigationQuery,
  pageBySlugQuery,
  settingsQuery,
} from "@/lib/api/queries";

/** Prefetch chrome data needed by the 404 / not-found experience. */
export async function prefetchNotFoundData(
  queryClient: QueryClient,
  locale: string,
) {
  await Promise.all([
    queryClient.prefetchQuery(navigationQuery(locale)),
    queryClient.prefetchQuery(settingsQuery(locale)),
  ]);
}

/**
 * Prefetch navigation, settings, and page-by-slug for a locale/slug.
 * @returns `{ found: false }` when the page fetch fails (404 path).
 */
export async function prefetchPageData(
  queryClient: QueryClient,
  locale: string,
  slug: string,
): Promise<{ found: boolean }> {
  await prefetchNotFoundData(queryClient, locale);

  try {
    await queryClient.fetchQuery(pageBySlugQuery(locale, slug));
    return { found: true };
  } catch {
    return { found: false };
  }
}
