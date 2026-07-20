import { describe, expect, it } from "vitest";
import { negotiateLocale } from "@/lib/i18n/negotiate";

describe("negotiateLocale", () => {
  it("defaults to en when header is missing", () => {
    expect(negotiateLocale(null)).toBe("en");
    expect(negotiateLocale("")).toBe("en");
  });

  it("matches English variants", () => {
    expect(negotiateLocale("en-US,en;q=0.9")).toBe("en");
    expect(negotiateLocale("en-GB")).toBe("en");
  });

  it("matches Simplified Chinese", () => {
    expect(negotiateLocale("zh-CN,zh;q=0.9,en;q=0.8")).toBe("sc");
    expect(negotiateLocale("zh-Hans")).toBe("sc");
    expect(negotiateLocale("zh")).toBe("sc");
  });

  it("matches Traditional Chinese", () => {
    expect(negotiateLocale("zh-TW,zh;q=0.9,en;q=0.8")).toBe("tc");
    expect(negotiateLocale("zh-HK")).toBe("tc");
    expect(negotiateLocale("zh-Hant")).toBe("tc");
  });

  it("respects quality values", () => {
    expect(negotiateLocale("en;q=0.5,zh-TW;q=0.9")).toBe("tc");
  });
});
