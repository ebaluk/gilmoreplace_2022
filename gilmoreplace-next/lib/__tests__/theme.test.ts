import { describe, it, expect } from "vitest";
import { normalizeTheme, themeClassName, type ResolvedTheme } from "@/lib/theme";

describe("normalizeTheme", () => {
  it("returns null for undefined input", () => {
    expect(normalizeTheme(undefined)).toBeNull();
  });

  it("returns null for null input", () => {
    expect(normalizeTheme(null)).toBeNull();
  });

  it("returns null for zero (falsy) input", () => {
    expect(normalizeTheme(0)).toBeNull();
  });

  it("normalizes a number theme ID with known CSS class", () => {
    expect(normalizeTheme(1)).toEqual({ id: 1, css_class: "site-0" });
  });

  it("normalizes a number theme ID with known CSS class (id=2)", () => {
    expect(normalizeTheme(2)).toEqual({ id: 2, css_class: "site-1" });
  });

  it("normalizes a number theme ID with unknown CSS class", () => {
    expect(normalizeTheme(99)).toEqual({ id: 99, css_class: null });
  });

  it("passes through a ResolvedTheme with css_class", () => {
    const theme: ResolvedTheme = { id: 3, css_class: "custom" };
    expect(normalizeTheme(theme)).toBe(theme);
  });

  it("fills missing css_class from lookup for ResolvedTheme without css_class", () => {
    expect(normalizeTheme({ id: 1, css_class: null })).toEqual({
      id: 1,
      css_class: "site-0",
    });
  });
});

describe("themeClassName", () => {
  it("returns empty string for undefined", () => {
    expect(themeClassName(undefined)).toBe("");
  });

  it("returns empty string for null", () => {
    expect(themeClassName(null)).toBe("");
  });

  it("returns themed class + css class for known ID", () => {
    expect(themeClassName(1)).toBe("themed-1 site-0");
  });

  it("returns only themed class for unknown ID (no CSS class)", () => {
    expect(themeClassName(99)).toBe("themed-99");
  });

  it("returns class from ResolvedTheme", () => {
    expect(themeClassName({ id: 2, css_class: "site-1" })).toBe("themed-2 site-1");
  });
});
