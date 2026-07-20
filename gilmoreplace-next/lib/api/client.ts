/**
 * Headless Wagtail API client used by Next.js (SSR + browser).
 *
 * Base URL: `WAGTAIL_API_URL` on the server; on the client prefers
 * `NEXT_PUBLIC_API_URL` + `/api/v2` (public origin behind nginx).
 * Paths below are relative to that base (e.g. `/headless/settings/`).
 */

import { apiLocaleFromRoute } from "@/lib/i18n/config";

/** Resolve API origin for the current runtime (browser vs Node). */
function resolveApiUrl(): string {
  // Browser: use public origin (WAGTAIL_API_URL is internal Docker hostname at build time).
  if (typeof window !== "undefined") {
    const publicOrigin = process.env.NEXT_PUBLIC_API_URL;
    if (publicOrigin) {
      return `${publicOrigin.replace(/\/$/, "")}/api/v2`;
    }
  }
  return process.env.WAGTAIL_API_URL || "http://localhost:8000/api/v2";
}

/** Map a Next.js locale segment (`en` / `sc` / `tc`) to Wagtail API locale (`en-us`, …). */
export function normalizeLocale(locale: string): string {
  return apiLocaleFromRoute(locale);
}

/**
 * GET JSON from the headless API (ISR `revalidate: 60` for Next fetch cache).
 * Pass `{ cache: "no-store" }` for draft preview (no ISR).
 * @throws Error when the response is not OK
 */
async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${resolveApiUrl()}${path}`;
  const cache = options?.cache;
  const res = await fetch(url, {
    ...options,
    ...(cache === "no-store"
      ? { cache: "no-store" }
      : { next: { revalidate: 60 } }),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText} for ${url}`);
  }
  return res.json();
}

/** Response of `GET /headless/pages/?locale=` — lightweight page list for SSG. */
export interface PageListResponse {
  pages: {
    id: number;
    title: string;
    slug: string;
    url: string;
    seo_title: string;
    search_description: string;
    show_in_menus: boolean;
    content_type: string;
    language_code: string;
  }[];
}

/** Response of `GET /headless/navigation/`. */
export interface NavigationResponse {
  items: NavItem[];
}

/** Nested menu node (up to two child levels from the API). */
export interface NavItem {
  id: number;
  title: string;
  slug: string;
  url: string;
  show_navbar: boolean;
  children: NavItem[];
}

/** Response of `GET /headless/settings/?locale=`. */
export interface SettingsResponse {
  site_settings: {
    caption: string;
    logo: import("@/types/page").ImageData | null;
    ga_view_id: number;
  };
  page_meta: {
    site_name: string;
    default_title: string | null;
    default_description: string | null;
    default_keywords: string | null;
    default_image: import("@/types/page").ImageData | null;
    fb_app_id: string | null;
  };
  root_page?: RootPageSettings | null;
  language_roots?: LanguageRoot[];
}

/** Language-root chrome: contact, footer, 404, header promo. */
export interface RootPageSettings {
  id: number;
  phone: string;
  email: string;
  footer_legal: string;
  contact_page_url: string | null;
  penthouse_collections_url: string | null;
  header_promo_box?: {
    title: string;
    page_id: number;
  } | null;
  footer_social_links: {
    title: string;
    fontawesome_icon: string;
    link: string;
    new_window: boolean;
  }[];
  page_404_title?: string;
  page_404_text?: string;
  page_404_image?: import("@/types/page").ImageData | null;
}

/** One CMS language root for the language switcher. */
export interface LanguageRoot {
  language_code: string;
  url: string;
  label: string;
}

/** Response of `GET /headless/themes/`. */
export interface ThemesResponse {
  themes: (import("@/types/page").CssTheme & { rendered_css?: string })[];
}

/** Response of `GET /headless/towers/`. */
export interface TowerDataResponse {
  bedroom_types: {
    id: number;
    title: string;
    title_zh_hans: string;
    title_zh_hant: string;
    sort_order: number;
  }[];
  penthouse_types: {
    id: number;
    title: string;
    title_zh_hans: string;
    title_zh_hant: string;
    sort_order: number;
  }[];
  shared_blocks: {
    id: number;
    title: string;
    stream_field: import("@/types/page").StreamFieldBlock[];
  }[];
}

/**
 * Fetch a page by Wagtail slug for the given Next.js locale segment.
 * GET /headless/pages/by-slug/?slug=&locale=
 */
export function getPageBySlug(
  slug: string,
  locale: string
): Promise<import("@/types/page").WagtailPage> {
  return fetchAPI(`/headless/pages/by-slug/?slug=${encodeURIComponent(slug)}&locale=${normalizeLocale(locale)}`);
}

/**
 * Fetch a draft page for Wagtail admin preview.
 * GET /headless/pages/preview/?content_type=&token=
 * Sends ``X-Preview-Secret`` from server env (never expose to the browser).
 */
export function getPagePreview(
  contentType: string,
  token: string
): Promise<import("@/types/page").WagtailPage> {
  const qs = new URLSearchParams({ content_type: contentType, token });
  const secret =
    process.env.PREVIEW_SECRET || process.env.REVALIDATION_SECRET || "";
  return fetchAPI(`/headless/pages/preview/?${qs.toString()}`, {
    cache: "no-store",
    headers: secret ? { "X-Preview-Secret": secret } : {},
  });
}

/** Fetch a page by numeric Wagtail id. GET /headless/pages/<id>/ */
export function getPageById(
  id: number
): Promise<import("@/types/page").WagtailPage> {
  return fetchAPI(`/headless/pages/${id}/`);
}

/** List live pages under a language root. GET /headless/pages/?locale= */
export function getAllPages(locale: string): Promise<PageListResponse> {
  return fetchAPI(`/headless/pages/?locale=${normalizeLocale(locale)}`);
}

/** Menu tree for a locale. GET /headless/navigation/?locale= */
export function getNavigation(locale: string): Promise<NavigationResponse> {
  return fetchAPI(`/headless/navigation/?locale=${normalizeLocale(locale)}`);
}

/** Site + language-root settings. GET /headless/settings/?locale= */
export function getSettings(locale: string): Promise<SettingsResponse> {
  return fetchAPI(`/headless/settings/?locale=${normalizeLocale(locale)}`);
}

/** All CSS themes. GET /headless/themes/ */
export function getThemes(): Promise<ThemesResponse> {
  return fetchAPI("/headless/themes/");
}

/** Bedroom/penthouse types and shared blocks. GET /headless/towers/ */
export function getTowerData(): Promise<TowerDataResponse> {
  return fetchAPI("/headless/towers/");
}

/** Form schema for a WtForm id. GET /headless/forms/<id>/ */
export function getForm(formId: number): Promise<FormResponse> {
  return fetchAPI(`/headless/forms/${formId}/`);
}

/** WtForm detail payload including fields and reCAPTCHA. */
export interface FormResponse {
  id: number;
  title: string;
  submit_url: string;
  fields: FormField[];
  recaptcha_site_key: string;
  enable_recaptcha?: boolean;
}

export interface FormFieldChoice {
  value: string;
  label: string;
}

/** One CMS form field as returned by the headless API. */
export interface FormField {
  id: number;
  label: string;
  field_type: string;
  required: boolean;
  choices: string | null;
  choices_list?: FormFieldChoice[];
  default_value: string | null;
  help_text: string | null;
  clean_name: string;
  add_css_class?: string;
  num?: number;
}
