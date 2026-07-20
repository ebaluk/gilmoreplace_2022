/**
 * Homepage promo visit/reload counters — show every Nth entry.
 */

import {
  getPageLoadId,
  hasClientNavigated,
  isHomepageClientEntry,
  isPageReload,
  onDocumentReady,
} from "@/lib/client-navigation";

export const PROMO_SHOW_EVERY_N = 4;

const VISITS_KEY = "gilmoreplace:homepage-visits";
const RELOADS_KEY = "gilmoreplace:homepage-reloads";
const SHOW_DECISION_PREFIX = "gilmoreplace:promo-show:";

function readCount(key: string): number {
  try {
    const n = parseInt(localStorage.getItem(key) || "0", 10);
    return Number.isFinite(n) ? n : 0;
  } catch {
    return 0;
  }
}

function incrementCount(key: string): number {
  const next = readCount(key) + 1;
  try {
    localStorage.setItem(key, String(next));
  } catch {
    // Ignore storage errors (private mode, etc.)
  }
  return next;
}

function isPromoNth(count: number): boolean {
  return count > 0 && count % PROMO_SHOW_EVERY_N === 0;
}

function showDecisionKey(): string {
  return `${SHOW_DECISION_PREFIX}${getPageLoadId()}`;
}

/** Read homepage visit counter from localStorage. */
export function getHomepageVisitCount(): number {
  return readCount(VISITS_KEY);
}

/** Read homepage reload counter from localStorage. */
export function getHomepageReloadCount(): number {
  return readCount(RELOADS_KEY);
}

/**
 * Homepage promo: every Nth full-page visit and every Nth homepage reload.
 * Wagtail still controls which pages render the modal (page.promo_box).
 */
/** Increment counters and return true every Nth homepage entry/reload. */
export function shouldAutoShowHomepagePromo(): boolean {
  if (typeof window === "undefined") return false;

  onDocumentReady();

  if (isHomepageClientEntry() || hasClientNavigated()) {
    return false;
  }

  const decisionKey = showDecisionKey();
  const existing = sessionStorage.getItem(decisionKey);
  if (existing !== null) {
    return existing === "1";
  }

  let show = false;
  if (isPageReload()) {
    show = isPromoNth(incrementCount(RELOADS_KEY));
  } else {
    show = isPromoNth(incrementCount(VISITS_KEY));
  }

  sessionStorage.setItem(decisionKey, show ? "1" : "0");
  return show;
}
