import { describe, expect, it } from "vitest";
import { localeAndSlugFromPathname } from "@/lib/hero-video-preload";

describe("localeAndSlugFromPathname", () => {
  it("parses homepage", () => {
    expect(localeAndSlugFromPathname("/en")).toEqual({ locale: "en", slug: "" });
    expect(localeAndSlugFromPathname("/en/")).toEqual({ locale: "en", slug: "" });
  });

  it("parses nested slug", () => {
    expect(localeAndSlugFromPathname("/en/penthouses")).toEqual({
      locale: "en",
      slug: "penthouses",
    });
  });

  it("returns null for unknown locale", () => {
    expect(localeAndSlugFromPathname("/fr")).toBeNull();
  });
});
