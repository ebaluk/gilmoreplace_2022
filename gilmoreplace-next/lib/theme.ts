/**
 * Normalize Wagtail CSS theme snippets to `themed-{id}` / layout class names.
 */

/** Theme id plus optional legacy layout CSS class (`site-0`, `site-1`, …). */
export interface ResolvedTheme {
  id: number;
  css_class: string | null;
}

/** Map theme snippet IDs to layout CSS classes when API returns only an integer. */
const THEME_CSS_CLASS: Record<number, string> = {
  1: "site-0",
  2: "site-1",
};

/** Coerce API theme (id or object) into a resolved theme with css_class fallback. */
export function normalizeTheme(
  theme?: number | ResolvedTheme | null
): ResolvedTheme | null {
  if (!theme) return null;
  if (typeof theme === "number") {
    return {
      id: theme,
      css_class: THEME_CSS_CLASS[theme] ?? null,
    };
  }
  if (theme.css_class) return theme;
  return {
    id: theme.id,
    css_class: THEME_CSS_CLASS[theme.id] ?? null,
  };
}

/** Space-joined class list: `themed-{id}` and optional `css_class`. */
export function themeClassName(theme?: number | ResolvedTheme | null): string {
  const resolved = normalizeTheme(theme);
  if (!resolved) return "";
  return [
    resolved.id ? `themed-${resolved.id}` : "",
    resolved.css_class || "",
  ]
    .filter(Boolean)
    .join(" ");
}
