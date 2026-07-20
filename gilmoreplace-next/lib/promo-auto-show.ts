/**
 * Cross-component pub/sub for homepage promo auto-open (session pending flag).
 */

const listeners = new Set<() => void>();
const PENDING_KEY = "gilmoreplace:promo-auto-pending";

/** Subscribe to promo auto-show requests; returns unsubscribe. */
export function onPromoAutoShowRequest(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Mark pending + notify listeners (called when visit cadence says show). */
export function requestPromoAutoShow(): void {
  if (typeof sessionStorage !== "undefined") {
    sessionStorage.setItem(PENDING_KEY, "1");
  }
  listeners.forEach((listener) => listener());
}

/** Consume session pending flag; true once per pending request. */
export function consumePendingPromoAutoShow(): boolean {
  if (typeof sessionStorage === "undefined") return false;
  if (sessionStorage.getItem(PENDING_KEY) !== "1") return false;
  sessionStorage.removeItem(PENDING_KEY);
  return true;
}
