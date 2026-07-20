/**
 * Next.js route locales (`en` / `sc` / `tc`) and mappings to Wagtail / HTML lang.
 */

export const locales = ["en", "sc", "tc"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

export const localeLabels: Record<Locale, string> = {
  en: "EN",
  sc: "简",
  tc: "繁",
};

/** BCP47 HTML lang attribute for each Next.js route segment */
export const routeToHtmlLang: Record<Locale, string> = {
  en: "en",
  sc: "zh-Hans",
  tc: "zh-Hant",
};

/** BCP47 `lang` for `<html>` from a Next route segment. */
export function htmlLangFromRoute(routeLocale: string): string {
  return routeToHtmlLang[routeLocale as Locale] ?? "en";
}

/** Django/Wagtail API locale for each Next.js route segment */
export const routeToApiLocale: Record<Locale, string> = {
  en: "en-us",
  sc: "zh-hans",
  tc: "zh-hant",
};

/** Wagtail API `locale` query value for a Next route segment. */
export function apiLocaleFromRoute(routeLocale: string): string {
  return routeToApiLocale[routeLocale as Locale] ?? routeLocale;
}

/** Compare Next segment to a Wagtail `language_code` (after mapping). */
export function isSameLocale(routeLocale: string, apiLanguageCode: string): boolean {
  return apiLocaleFromRoute(routeLocale) === apiLanguageCode;
}

/** Short UI label for a locale or Wagtail language code. */
export function localeLabel(code: string): string {
  if (code in localeLabels) {
    return localeLabels[code as Locale];
  }
  if (code === "en-us") {
    return localeLabels.en;
  }
  if (code === "zh-hans") {
    return localeLabels.sc;
  }
  if (code === "zh-hant") {
    return localeLabels.tc;
  }
  return code;
}

/** First path segment as Locale, or `defaultLocale`. */
export function localeFromPathname(pathname: string): Locale {
  const segment = pathname.split("/").filter(Boolean)[0];
  if (segment && locales.includes(segment as Locale)) {
    return segment as Locale;
  }
  return defaultLocale;
}
