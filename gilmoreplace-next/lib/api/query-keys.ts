/**
 * Canonical TanStack Query keys for headless API data.
 * Keep in sync with `queries.ts` and SSR `prefetch-page.ts`.
 */
export const queryKeys = {
  pages: {
    all: (locale: string) => ["pages", locale] as const,
    bySlug: (locale: string, slug: string) =>
      ["pages", locale, slug] as const,
  },
  navigation: (locale: string) => ["navigation", locale] as const,
  settings: (locale: string) => ["settings", locale] as const,
  form: (formId: number) => ["form", formId] as const,
  themes: () => ["themes"] as const,
  towerData: () => ["towerData"] as const,
};
