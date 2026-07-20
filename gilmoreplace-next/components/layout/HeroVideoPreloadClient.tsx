"use client";


/**
 * Site layout: HeroVideoPreloadClient.
 */
import { usePathname } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useLayoutEffect } from "react";
import { queryKeys } from "@/lib/api/query-keys";
import { pageBySlugQuery } from "@/lib/api/queries";
import {
  isHomepageClientEntry,
  onDocumentReady,
  trackPathnameChange,
} from "@/lib/client-navigation";
import { localeAndSlugFromPathname, preloadHeroForPathname } from "@/lib/hero-video-preload";
import { requestPromoAutoShow } from "@/lib/promo-auto-show";
import { shouldAutoShowHomepagePromo } from "@/lib/promo-homepage";
import type { WagtailPage } from "@/types/page";

const PROMO_AUTO_FIRED_PREFIX = "gilmoreplace:promo-auto-fired:";

function promoAutoFiredKey(): string {
  return `${PROMO_AUTO_FIRED_PREFIX}${typeof window !== "undefined" ? performance.timeOrigin : "server"}`;
}

function isDevPromoForced(): boolean {
  if (process.env.NODE_ENV !== "development") return false;
  return new URLSearchParams(window.location.search).has("promo");
}

async function maybeScheduleHomepagePromo(
  pathname: string,
  queryClient: ReturnType<typeof useQueryClient>,
): Promise<void> {
  const parsed = localeAndSlugFromPathname(pathname);
  if (!parsed || parsed.slug !== "") return;

  if (isDevPromoForced()) {
    requestPromoAutoShow();
    return;
  }

  if (isHomepageClientEntry()) return;
  if (sessionStorage.getItem(promoAutoFiredKey()) === "1") return;

  let page = queryClient.getQueryData<WagtailPage>(
    queryKeys.pages.bySlug(parsed.locale, ""),
  );
  if (!page) {
    try {
      page = await queryClient.fetchQuery(pageBySlugQuery(parsed.locale, ""));
    } catch {
      return;
    }
  }

  if (!page.promo_box || page.content_type !== "languagerootpage") return;
  if (!shouldAutoShowHomepagePromo()) return;

  sessionStorage.setItem(promoAutoFiredKey(), "1");
  requestPromoAutoShow();
}

/** Route-level side effects: navigation tracking, hero preload, homepage promo scheduling. */
export function HeroVideoPreloadClient() {
  const pathname = usePathname();
  const queryClient = useQueryClient();

  useLayoutEffect(() => {
    onDocumentReady();
    trackPathnameChange(pathname);
    preloadHeroForPathname(queryClient, pathname);
  }, [pathname, queryClient]);

  useEffect(() => {
    void maybeScheduleHomepagePromo(pathname, queryClient);
  }, [pathname, queryClient]);

  return null;
}
