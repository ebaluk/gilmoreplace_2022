import { describe, it, expect } from "vitest";
import {
  locales,
  defaultLocale,
  localeLabels,
  htmlLangFromRoute,
  apiLocaleFromRoute,
  isSameLocale,
  localeLabel,
  localeFromPathname,
} from "@/lib/i18n/config";

describe("constants", () => {
  it("has three locales", () => {
    expect(locales).toEqual(["en", "sc", "tc"]);
  });

  it("default locale is en", () => {
    expect(defaultLocale).toBe("en");
  });

  it("localeLabels has all locales", () => {
    expect(localeLabels).toEqual({ en: "EN", sc: "简", tc: "繁" });
  });
});

describe("htmlLangFromRoute", () => {
  it('returns "en" for en', () => {
    expect(htmlLangFromRoute("en")).toBe("en");
  });

  it('returns "zh-Hans" for sc', () => {
    expect(htmlLangFromRoute("sc")).toBe("zh-Hans");
  });

  it('returns "zh-Hant" for tc', () => {
    expect(htmlLangFromRoute("tc")).toBe("zh-Hant");
  });

  it('falls back to "en" for unknown locale', () => {
    expect(htmlLangFromRoute("fr")).toBe("en");
  });

  it('falls back to "en" for empty string', () => {
    expect(htmlLangFromRoute("")).toBe("en");
  });
});

describe("apiLocaleFromRoute", () => {
  it('returns "en-us" for en', () => {
    expect(apiLocaleFromRoute("en")).toBe("en-us");
  });

  it('returns "zh-hans" for sc', () => {
    expect(apiLocaleFromRoute("sc")).toBe("zh-hans");
  });

  it('returns "zh-hant" for tc', () => {
    expect(apiLocaleFromRoute("tc")).toBe("zh-hant");
  });

  it("passes through unknown locale unchanged", () => {
    expect(apiLocaleFromRoute("fr")).toBe("fr");
  });
});

describe("isSameLocale", () => {
  it("matches route en with API en-us", () => {
    expect(isSameLocale("en", "en-us")).toBe(true);
  });

  it("matches route sc with API zh-hans", () => {
    expect(isSameLocale("sc", "zh-hans")).toBe(true);
  });

  it("does not match route en with API zh-hans", () => {
    expect(isSameLocale("en", "zh-hans")).toBe(false);
  });

  it("does not match different locales", () => {
    expect(isSameLocale("sc", "en-us")).toBe(false);
  });
});

describe("localeLabel", () => {
  it('returns "EN" for en', () => {
    expect(localeLabel("en")).toBe("EN");
  });

  it('returns "简" for sc', () => {
    expect(localeLabel("sc")).toBe("简");
  });

  it('returns "繁" for tc', () => {
    expect(localeLabel("tc")).toBe("繁");
  });

  it('returns "EN" for en-us (API code fallback)', () => {
    expect(localeLabel("en-us")).toBe("EN");
  });

  it('returns "简" for zh-hans (API code fallback)', () => {
    expect(localeLabel("zh-hans")).toBe("简");
  });

  it('returns "繁" for zh-hant (API code fallback)', () => {
    expect(localeLabel("zh-hant")).toBe("繁");
  });

  it("returns raw code for truly unknown code", () => {
    expect(localeLabel("de")).toBe("de");
  });
});

describe("localeFromPathname", () => {
  it("extracts en from pathname", () => {
    expect(localeFromPathname("/en/about")).toBe("en");
  });

  it("extracts sc from pathname", () => {
    expect(localeFromPathname("/sc/about")).toBe("sc");
  });

  it("extracts tc from pathname", () => {
    expect(localeFromPathname("/tc/about")).toBe("tc");
  });

  it("falls back to en for unknown locale prefix", () => {
    expect(localeFromPathname("/fr/about")).toBe("en");
  });

  it("falls back to en for root path", () => {
    expect(localeFromPathname("/")).toBe("en");
  });

  it("falls back to en for empty string", () => {
    expect(localeFromPathname("")).toBe("en");
  });
});
