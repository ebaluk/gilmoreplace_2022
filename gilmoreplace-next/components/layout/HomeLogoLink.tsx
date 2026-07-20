"use client";


/**
 * Site layout: HomeLogoLink.
 */
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { preloadHomepageHeroFromCache } from "@/lib/hero-video-preload";
import type { Locale } from "@/lib/i18n/config";

interface HomeLogoLinkProps {
  locale: string;
}

/** Logo link back to the language-root homepage. */
export function HomeLogoLink({ locale }: HomeLogoLinkProps) {
  const queryClient = useQueryClient();

  const warmHomepageVideo = () => {
    preloadHomepageHeroFromCache(queryClient, locale as Locale);
  };

  return (
    <Link
      href={`/${locale}`}
      className="logo router-link-active"
      onMouseEnter={warmHomepageVideo}
      onFocus={warmHomepageVideo}
    >
      <img src="/images/logo.svg" alt="Gilmore Place" />
    </Link>
  );
}
