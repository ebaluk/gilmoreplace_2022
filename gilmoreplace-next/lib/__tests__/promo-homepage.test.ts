import { afterEach, describe, expect, it, vi } from "vitest";
import {
  hasClientNavigated,
  isHomepageClientEntry,
  onDocumentReady,
  trackPathnameChange,
} from "@/lib/client-navigation";
import {
  getHomepageReloadCount,
  getHomepageVisitCount,
  shouldAutoShowHomepagePromo,
} from "@/lib/promo-homepage";

let loadCounter = 0;

function beginDocument(type: "navigate" | "reload", startTime: number): void {
  loadCounter += 1;
  sessionStorage.removeItem("gilmoreplace:doc-id");
  vi.spyOn(performance, "getEntriesByType").mockReturnValue([
    { type, startTime } as PerformanceNavigationTiming,
  ]);
  Object.defineProperty(performance, "timeOrigin", {
    value: 1_000_000 + loadCounter,
    configurable: true,
  });
  onDocumentReady();
}

describe("client navigation", () => {
  afterEach(() => {
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it("tracks pathname changes as client navigation", () => {
    beginDocument("navigate", 1);
    trackPathnameChange("/en");
    trackPathnameChange("/en/penthouses");
    expect(hasClientNavigated()).toBe(true);
  });

  it("marks homepage client entry separately from global client nav", () => {
    beginDocument("navigate", 1);
    trackPathnameChange("/en");
    expect(isHomepageClientEntry()).toBe(false);

    trackPathnameChange("/en/penthouses");
    trackPathnameChange("/en");
    expect(isHomepageClientEntry()).toBe(true);
  });
});

describe("shouldAutoShowHomepagePromo", () => {
  afterEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("does not show on visits 1–3", () => {
    for (let i = 1; i <= 3; i++) {
      sessionStorage.clear();
      beginDocument("navigate", i);
      trackPathnameChange("/en");
      expect(shouldAutoShowHomepagePromo()).toBe(false);
      expect(getHomepageVisitCount()).toBe(i);
      vi.restoreAllMocks();
    }
  });

  it("shows on the 4th homepage visit", () => {
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    sessionStorage.clear();
    beginDocument("navigate", 4);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageVisitCount()).toBe(4);
  });

  it("shows on the 4th homepage reload", () => {
    localStorage.setItem("gilmoreplace:homepage-reloads", "3");
    sessionStorage.clear();
    beginDocument("reload", 99);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageReloadCount()).toBe(4);
  });

  it("does not show on reloads 1–3", () => {
    for (let i = 1; i <= 3; i++) {
      sessionStorage.clear();
      beginDocument("reload", i);
      trackPathnameChange("/en");
      expect(shouldAutoShowHomepagePromo()).toBe(false);
      expect(getHomepageReloadCount()).toBe(i);
      vi.restoreAllMocks();
    }
  });

  it("does not show every reload after the 4th", () => {
    localStorage.setItem("gilmoreplace:homepage-reloads", "3");
    sessionStorage.clear();
    beginDocument("reload", 40);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageReloadCount()).toBe(4);

    sessionStorage.clear();
    beginDocument("reload", 41);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(false);
    expect(getHomepageReloadCount()).toBe(5);
  });

  it("does not show after in-app navigation to homepage", () => {
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    beginDocument("navigate", 10);
    trackPathnameChange("/en/penthouses");
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(false);
    expect(getHomepageVisitCount()).toBe(3);
  });

  it("does not show again after client navigation back from a 4th-visit promo", () => {
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    beginDocument("navigate", 50);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageVisitCount()).toBe(4);

    trackPathnameChange("/en/penthouses");
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(false);
    expect(getHomepageVisitCount()).toBe(4);
  });

  it("shows after a fresh full load even if client-nav was set earlier in the tab", () => {
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    beginDocument("navigate", 10);
    trackPathnameChange("/en/penthouses");
    trackPathnameChange("/en");

    sessionStorage.clear();
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    beginDocument("navigate", 11);
    trackPathnameChange("/en");

    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageVisitCount()).toBe(4);
  });

  it("does not double-count on component remount", () => {
    localStorage.setItem("gilmoreplace:homepage-visits", "3");
    beginDocument("navigate", 42);
    trackPathnameChange("/en");
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(shouldAutoShowHomepagePromo()).toBe(true);
    expect(getHomepageVisitCount()).toBe(4);
  });

  it("shows on visits 4 and 8", () => {
    const results: boolean[] = [];
    for (let visit = 1; visit <= 8; visit++) {
      sessionStorage.clear();
      beginDocument("navigate", visit);
      trackPathnameChange("/en");
      results.push(shouldAutoShowHomepagePromo());
      vi.restoreAllMocks();
    }
    expect(results).toEqual([false, false, false, true, false, false, false, true]);
  });
});
