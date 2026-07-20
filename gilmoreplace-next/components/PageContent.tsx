"use client";

/**
 * Client page shell: useQuery page/settings/nav and render PageRenderer or 404.
 */
import { useQuery } from "@tanstack/react-query";
import { notFound } from "next/navigation";
import { PageRenderer } from "@/components/PageRenderer";
import {
  navigationQuery,
  pageBySlugQuery,
  settingsQuery,
} from "@/lib/api/queries";

interface PageContentProps {
  locale: string;
  slug: string;
}

/** Fetches page by locale+slug and renders the marketing page. */
export function PageContent({ locale, slug }: PageContentProps) {
  const pageQuery = useQuery(pageBySlugQuery(locale, slug));
  const navQuery = useQuery(navigationQuery(locale));
  const settingsQueryResult = useQuery(settingsQuery(locale));

  const isNotFound = pageQuery.isError && pageQuery.error?.message?.includes("404");

  if (isNotFound) {
    notFound();
  }

  if (
    pageQuery.isPending ||
    navQuery.isPending ||
    settingsQueryResult.isPending
  ) {
    return <div className="page-loading" aria-busy="true" />;
  }

  if (pageQuery.isError) {
    return (
      <div className="page-error">
        <p>Unable to load page. Please try again later.</p>
      </div>
    );
  }

  const page = pageQuery.data;
  const nav = navQuery.data;
  const settings = settingsQueryResult.data;

  if (!page || !nav || !settings) {
    notFound();
  }

  return (
    <PageRenderer
      page={page}
      nav={nav.items ?? []}
      settings={settings}
      locale={locale}
    />
  );
}
