/**
 * Locale segment layout — keeps `<html lang>` in sync with the route.
 */

interface LocaleLayoutProps {
  children: React.ReactNode;
  params: { locale: string };
}

import { HtmlLangUpdater } from "@/components/layout/HtmlLangUpdater";

/** Wraps locale pages and updates document language. */
export default function LocaleLayout({
  children,
  params: { locale },
}: LocaleLayoutProps) {
  return (
    <>
      <HtmlLangUpdater locale={locale} />
      {children}
    </>
  );
}
