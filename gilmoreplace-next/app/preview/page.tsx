/**
 * Wagtail admin headless preview — renders draft at this URL (no redirect to live path).
 * Opened by wagtail-headless-preview: /preview?content_type=…&token=…
 */

import { PageRenderer } from "@/components/PageRenderer";
import { PreviewLiveRefresh } from "@/components/PreviewLiveRefresh";
import { getNavigation, getPagePreview, getSettings } from "@/lib/api/client";
import {
  defaultLocale,
  type Locale,
  routeToApiLocale,
} from "@/lib/i18n/config";

export const dynamic = "force-dynamic";

function localeFromPageLanguage(languageCode: string | undefined): Locale {
  if (!languageCode) return defaultLocale;
  const entry = (
    Object.entries(routeToApiLocale) as [Locale, string][]
  ).find(([, api]) => api === languageCode);
  return entry?.[0] ?? defaultLocale;
}

interface PreviewPageProps {
  searchParams: { content_type?: string; token?: string };
}

export default async function PreviewPage({ searchParams }: PreviewPageProps) {
  const contentType = searchParams.content_type;
  const token = searchParams.token;

  if (!contentType || !token) {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>Preview</h1>
        <p>Missing <code>content_type</code> or <code>token</code>.</p>
      </main>
    );
  }

  let page;
  try {
    page = await getPagePreview(contentType, token);
  } catch {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>Preview unavailable</h1>
        <p>Invalid or expired preview token.</p>
      </main>
    );
  }

  const locale = localeFromPageLanguage(page.language_code);
  const [nav, settings] = await Promise.all([
    getNavigation(locale),
    getSettings(locale),
  ]);

  return (
    <>
      <PreviewLiveRefresh />
      <PageRenderer
        page={page}
        nav={nav.items ?? []}
        settings={settings}
        locale={locale}
      />
    </>
  );
}
