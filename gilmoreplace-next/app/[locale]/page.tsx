/**
 * Language-root homepage (`/{locale}`) — SSR prefetch + hydrate PageRenderer.
 */

import { dehydrate, HydrationBoundary } from "@tanstack/react-query";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { NotFoundPage } from "@/components/NotFoundPage";
import { PageRenderer } from "@/components/PageRenderer";
import { HeroVideoPreload } from "@/components/layout/HeroVideoPreload";
import { buildPageMetadata } from "@/components/seo/MetaTags";
import type { NavItem, SettingsResponse } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import { prefetchPageData } from "@/lib/api/prefetch-page";
import { pickHeroMp4Url, pickHeroPosterUrl } from "@/lib/hero-video";
import { isLocale } from "@/lib/i18n/config";
import { getQueryClient } from "@/lib/query-client";
import type { WagtailPage } from "@/types/page";

interface HomePageProps {
  params: { locale: string };
}

export async function generateMetadata({
  params: { locale },
}: HomePageProps): Promise<Metadata> {
  if (!isLocale(locale)) {
    return { title: "Gilmore Place" };
  }
  const queryClient = getQueryClient();
  const { found } = await prefetchPageData(queryClient, locale, "");
  if (!found) {
    return { title: "Page Not Found | Gilmore Place" };
  }
  const page = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(locale, ""),
  );
  if (!page) return { title: "Gilmore Place" };
  return buildPageMetadata({
    meta: page.meta,
    url: page.url,
    ogImage: page.meta?.og_image,
    fbAppId: page.meta?.fb_app_id,
  });
}

/** Prefetch empty slug for the language root and render the page shell. */
export default async function HomePage({ params: { locale } }: HomePageProps) {
  if (!isLocale(locale)) {
    notFound();
  }

  const queryClient = getQueryClient();
  const { found } = await prefetchPageData(queryClient, locale, "");

  if (!found) {
    return (
      <HydrationBoundary state={dehydrate(queryClient)}>
        <NotFoundPage locale={locale} />
      </HydrationBoundary>
    );
  }

  const page = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(locale, ""),
  );
  const nav = queryClient.getQueryData<{ items: NavItem[] }>(
    queryKeys.navigation(locale),
  );
  const settings = queryClient.getQueryData<SettingsResponse>(
    queryKeys.settings(locale),
  );

  if (!page || !nav || !settings) {
    notFound();
  }

  const mp4Url = pickHeroMp4Url(page.hero?.video);
  const posterUrl = pickHeroPosterUrl(page.hero?.video, page.hero?.images);

  return (
    <>
      <HeroVideoPreload mp4Url={mp4Url} posterUrl={posterUrl} />
      <HydrationBoundary state={dehydrate(queryClient)}>
        <PageRenderer
          page={page}
          nav={nav.items ?? []}
          settings={settings}
          locale={locale}
        />
      </HydrationBoundary>
    </>
  );
}
