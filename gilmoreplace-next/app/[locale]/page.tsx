/**
 * Language-root homepage (`/{locale}`) — SSR prefetch + hydrate PageContent.
 */

import { dehydrate, HydrationBoundary } from "@tanstack/react-query";
import { PageContent } from "@/components/PageContent";
import { HeroVideoPreload } from "@/components/layout/HeroVideoPreload";
import { queryKeys } from "@/lib/api/query-keys";
import { prefetchPageData } from "@/lib/api/prefetch-page";
import { pickHeroMp4Url, pickHeroPosterUrl } from "@/lib/hero-video";
import { getQueryClient } from "@/lib/query-client";
import type { WagtailPage } from "@/types/page";

interface HomePageProps {
  params: { locale: string };
}

/** Prefetch empty slug for the language root and render the page shell. */
export default async function HomePage({ params: { locale } }: HomePageProps) {
  const queryClient = getQueryClient();
  await prefetchPageData(queryClient, locale, "");

  const page = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(locale, ""),
  );
  const mp4Url = pickHeroMp4Url(page?.hero?.video);
  const posterUrl = pickHeroPosterUrl(page?.hero?.video, page?.hero?.images);

  return (
    <>
      <HeroVideoPreload mp4Url={mp4Url} posterUrl={posterUrl} />
      <HydrationBoundary state={dehydrate(queryClient)}>
        <PageContent locale={locale} slug="" />
      </HydrationBoundary>
    </>
  );
}
