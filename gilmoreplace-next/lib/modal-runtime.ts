/**
 * Body scroll-lock and Escape-key stack for overlays/modals.
 */

type EscapeHandler = () => void;

let scrollLockCount = 0;
let lockedScrollY = 0;

const escapeStack: EscapeHandler[] = [];
let escapeListenerAttached = false;

const SCROLL_KEYS = new Set([
  " ",
  "ArrowUp",
  "ArrowDown",
  "PageUp",
  "PageDown",
  "Home",
  "End",
]);

function ensureEscapeListener() {
  if (escapeListenerAttached) return;
  escapeListenerAttached = true;

  window.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const top = escapeStack[escapeStack.length - 1];
    if (top) top();
  });
}

/** Allow scrolling inside modal panels that need it (e.g. floorplan overlay). */
function isScrollAllowedTarget(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) return false;
  return Boolean(
    target.closest(
      [
        "[data-scroll-lock-scrollable]",
        ".section-plans .overlay",
        ".penthouses-widget .overlay",
      ].join(",")
    )
  );
}

function onWheel(event: WheelEvent) {
  if (isScrollAllowedTarget(event.target)) return;
  event.preventDefault();
}

function onTouchMove(event: TouchEvent) {
  if (isScrollAllowedTarget(event.target)) return;
  event.preventDefault();
}

function onKeyDown(event: KeyboardEvent) {
  if (!SCROLL_KEYS.has(event.key)) return;
  if (isScrollAllowedTarget(event.target)) return;
  // Allow typing in fields
  if (
    event.target instanceof HTMLElement &&
    (event.target.isContentEditable ||
      event.target.tagName === "INPUT" ||
      event.target.tagName === "TEXTAREA" ||
      event.target.tagName === "SELECT")
  ) {
    return;
  }
  event.preventDefault();
}

function onScroll() {
  if (window.scrollY === lockedScrollY) return;
  window.scrollTo({ top: lockedScrollY, left: 0, behavior: "auto" });
}

/**
 * Lock background scroll without touching body layout styles.
 * CSS overflow/position hacks caused top-jump / menu flash / layout shift.
 */
/** Nestable body scroll lock (reference-counted). */
export function lockBodyScroll(): void {
  if (typeof document === "undefined") return;
  if (scrollLockCount === 0) {
    lockedScrollY = window.scrollY;
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("keydown", onKeyDown, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });
  }
  scrollLockCount += 1;
}

/** Release one nest level of body scroll lock. */
export function unlockBodyScroll(): void {
  if (typeof document === "undefined") return;
  if (scrollLockCount <= 0) return;
  scrollLockCount -= 1;
  if (scrollLockCount !== 0) return;

  window.removeEventListener("wheel", onWheel);
  window.removeEventListener("touchmove", onTouchMove);
  window.removeEventListener("keydown", onKeyDown);
  window.removeEventListener("scroll", onScroll);
  window.scrollTo({ top: lockedScrollY, left: 0, behavior: "auto" });
}

/**
 * Stack-based ESC handling: only the topmost modal closes.
 * Returns an unsubscribe function (must be called on unmount).
 */
/** Push Escape handler; topmost runs first. Returns unsubscribe. */
export function pushEscapeHandler(handler: EscapeHandler): () => void {
  if (typeof window === "undefined") return () => {};
  ensureEscapeListener();
  escapeStack.push(handler);

  return () => {
    const idx = escapeStack.lastIndexOf(handler);
    if (idx >= 0) escapeStack.splice(idx, 1);
  };
}
