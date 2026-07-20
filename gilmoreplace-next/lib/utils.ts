/**
 * Small shared helpers (class names, media URLs).
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge class names with clsx + tailwind-merge. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Normalize CMS media URLs for `<img>` / video `src`.
 * Absolute and root-relative paths are left as-is (Next/nginx proxy in prod).
 */
export function formatImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  // Keep root-relative URLs (e.g. /media_files/...) as-is.
  // In dev, Next.js rewrites proxy these paths to the backend.
  // In prod, nginx serves /media_files and /static directly.
  if (url.startsWith("/")) return url;
  return `/${url}`;
}
