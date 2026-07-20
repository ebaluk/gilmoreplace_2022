/**
 * Catch-all CMS pages (`/{locale}/…`) with SSG params from the headless page list.
 */

import { dehydrate, HydrationBoundary } from "@tanstack/react-query";
import { NotFoundPage } from "@/components/NotFoundPage";
import { PageContent } from "@/components/PageContent";
import { HeroVideoPreload } from "@/components/layout/HeroVideoPreload";
import { getAllPages, type PageListResponse } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import { prefetchPageData } from "@/lib/api/prefetch-page";
import { pickHeroMp4Url, pickHeroPosterUrl } from "@/lib/hero-video";
import { locales } from "@/lib/i18n/config";
import { getQueryClient } from "@/lib/query-client";
import type { WagtailPage } from "@/types/page";

interface CatchAllPageProps {
  params: { locale: string; slug: string[] };
}

function getSlugFromUrl(url: string, locale: string): string[] {
  const prefix = `/${locale}/`;
  if (!url.startsWith(prefix)) return [];
  const rest = url.slice(prefix.length).replace(/\/$/, "");
  return rest ? rest.split("/") : [];
}

/** Build static paths from live pages under each language root. */
export async function generateStaticParams() {
  const paths: { locale: string; slug: string[] }[] = [];

  for (const locale of locales) {
    try {
      const data: PageListResponse = await getAllPages(locale);
      for (const page of data.pages) {
        const slugParts = getSlugFromUrl(page.url, locale);
        if (slugParts.length > 0) {
          paths.push({ locale, slug: slugParts });
        }
      }
    } catch {
      // skip
    }
  }
  return paths;
}

/** Prefetch by joined slug; render NotFoundPage when API miss. */
export default async function CatchAllPage({
  params: { locale, slug },
}: CatchAllPageProps) {
  const fullSlug = slug.join("/");
  const queryClient = getQueryClient();
  const { found } = await prefetchPageData(queryClient, locale, fullSlug);

  if (!found) {
    return (
      <HydrationBoundary state={dehydrate(queryClient)}>
        <NotFoundPage locale={locale} />
      </HydrationBoundary>
    );
  }

  const page = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(locale, fullSlug),
  );
  const mp4Url = pickHeroMp4Url(page?.hero?.video);
  const posterUrl = pickHeroPosterUrl(page?.hero?.video, page?.hero?.images);

  return (
    <>
      <HeroVideoPreload mp4Url={mp4Url} posterUrl={posterUrl} />
      <HydrationBoundary state={dehydrate(queryClient)}>
        <PageContent locale={locale} slug={fullSlug} />
      </HydrationBoundary>
    </>
  );
}
