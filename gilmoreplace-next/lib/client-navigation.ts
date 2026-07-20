/**
 * Session helpers for client-side navigation vs full reload (promo cadence).
 */

const CLIENT_NAV_KEY = "gilmoreplace:client-nav";
const LAST_PATH_KEY = "gilmoreplace:last-path";
const DOC_ID_KEY = "gilmoreplace:doc-id";
const HOME_ENTRY_PREFIX = "gilmoreplace:home-entry:";

/** Unique per full page load (new on every F5 or URL navigation). */
export function getPageLoadId(): string {
  if (typeof window === "undefined") return "server";
  return String(performance.timeOrigin);
}

/** @deprecated Use getPageLoadId(); kept for session keys in promo scheduling. */
export function getDocumentId(): string {
  return getPageLoadId();
}

function homeEntryKey(): string {
  return `${HOME_ENTRY_PREFIX}${getPageLoadId()}`;
}

export function isHomepageClientEntry(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(homeEntryKey()) === "client";
}

function isHomePath(pathname: string): boolean {
  const segments = pathname.split("/").filter(Boolean);
  return segments.length === 1;
}

/**
 * Reset per-document client state on a full navigation or reload.
 * Must run before pathname tracking and promo checks.
 */
export function onDocumentReady(): void {
  if (typeof window === "undefined") return;
  const loadId = getPageLoadId();
  if (sessionStorage.getItem(DOC_ID_KEY) === loadId) return;
  sessionStorage.setItem(DOC_ID_KEY, loadId);
  sessionStorage.removeItem(CLIENT_NAV_KEY);
  sessionStorage.removeItem(LAST_PATH_KEY);
  sessionStorage.removeItem(homeEntryKey());
}

export function markClientNavigation(): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(CLIENT_NAV_KEY, "1");
}

export function hasClientNavigated(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(CLIENT_NAV_KEY) === "1";
}

export function isPageReload(): boolean {
  if (typeof window === "undefined") return false;
  const entry = performance.getEntriesByType("navigation")[0] as
    | PerformanceNavigationTiming
    | undefined;
  return entry?.type === "reload";
}

/** Call when the App Router pathname changes (after onDocumentReady). */
export function trackPathnameChange(pathname: string): void {
  if (typeof window === "undefined") return;
  const lastPath = sessionStorage.getItem(LAST_PATH_KEY);
  const pathChanged = lastPath !== null && lastPath !== pathname;

  if (pathChanged) {
    markClientNavigation();
  }

  if (isHomePath(pathname)) {
    sessionStorage.setItem(homeEntryKey(), pathChanged ? "client" : "direct");
  }

  sessionStorage.setItem(LAST_PATH_KEY, pathname);
}
