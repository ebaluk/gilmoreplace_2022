/**
 * Body / #app class strings for legacy site.css color-theme and page-type hooks.
 */

import { type WagtailPage } from "@/types/page";

function isHomePage(page: WagtailPage): boolean {
  return page.content_type === "languagerootpage";
}

/** Classes for `#app` (content type, homepage, theme, color-theme). */
export function pageAppClass(page: WagtailPage): string {
  const contentType = page.content_type || "page";
  const themeClass = page.theme?.css_class ? `body-${page.theme.css_class}` : "";
  const colorTheme = `color-theme-${page.color_theme || "default"}`;
  return [contentType, isHomePage(page) ? "homepage" : "", themeClass, colorTheme]
    .filter(Boolean)
    .join(" ");
}

/** Theme classes applied to document.body (legacy CSS expects body.color-theme-*). */
export function pageBodyClass(page: WagtailPage): string {
  const themeClass = page.theme?.css_class ? `body-${page.theme.css_class}` : "";
  const colorTheme = `color-theme-${page.color_theme || "default"}`;
  return [themeClass, colorTheme].filter(Boolean).join(" ");
}
