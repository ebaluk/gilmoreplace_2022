/**
 * Pick a site Locale from an HTTP Accept-Language header (middleware).
 */

import { defaultLocale, type Locale, locales } from "./config";

const LOCALE_TAGS: Record<Locale, readonly string[]> = {
  en: ["en", "en-us", "en-gb", "en-au", "en-ca", "en-nz", "en-ie"],
  sc: ["zh-hans", "zh-cn", "zh-sg", "zh"],
  tc: ["zh-hant", "zh-tw", "zh-hk", "zh-mo"],
};

function parseAcceptLanguage(header: string | null): string[] {
  if (!header) return [];

  return header
    .split(",")
    .map((part) => {
      const [tag, ...params] = part.trim().split(";");
      const qParam = params.find((p) => p.trim().startsWith("q="));
      const q = qParam ? Number.parseFloat(qParam.trim().slice(2)) : 1;
      return { tag: tag.trim().toLowerCase(), q: Number.isNaN(q) ? 0 : q };
    })
    .sort((a, b) => b.q - a.q)
    .map((entry) => entry.tag);
}

function matchLocale(tag: string): Locale | null {
  for (const locale of locales) {
    if (LOCALE_TAGS[locale].includes(tag)) {
      return locale;
    }
  }

  const primary = tag.split("-")[0];
  for (const locale of locales) {
    if (LOCALE_TAGS[locale].includes(primary)) {
      return locale;
    }
  }

  return null;
}

/**
 * Negotiate preferred Locale from Accept-Language; falls back to `defaultLocale`.
 */
export function negotiateLocale(acceptLanguage: string | null): Locale {
  for (const tag of parseAcceptLanguage(acceptLanguage)) {
    const locale = matchLocale(tag);
    if (locale) return locale;
  }

  return defaultLocale;
}
