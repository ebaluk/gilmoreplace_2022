import { describe, expect, it } from "vitest";
import {
  isActivePath,
  isExternalStreamLink,
  resolveStreamLinkHref,
  wagtailUrlToNextPath,
} from "@/lib/urls";

describe("wagtailUrlToNextPath", () => {
  it("maps Wagtail locale prefixes to Next.js locales", () => {
    expect(wagtailUrlToNextPath("/en/commercial/shop/", "en")).toBe(
      "/en/commercial/shop",
    );
    expect(wagtailUrlToNextPath("/sc/discover/", "en")).toBe("/sc/discover");
    expect(wagtailUrlToNextPath("/tc/discover/", "en")).toBe("/tc/discover");
  });

  it("returns fallback locale for empty input", () => {
    expect(wagtailUrlToNextPath(null, "en")).toBe("/en");
    expect(wagtailUrlToNextPath("", "en")).toBe("/en");
  });

  it("handles language root paths", () => {
    expect(wagtailUrlToNextPath("/en/", "en")).toBe("/en");
  });

  it("passes document and media URLs through unchanged", () => {
    expect(
      wagtailUrlToNextPath(
        "/documents/106/gilmoreplace-feature-sheet.pdf",
        "en",
      ),
    ).toBe("/documents/106/gilmoreplace-feature-sheet.pdf");
    expect(wagtailUrlToNextPath("/media_files/images/foo.jpg", "en")).toBe(
      "/media_files/images/foo.jpg",
    );
  });
});

describe("isActivePath", () => {
  it("matches exact and nested paths", () => {
    expect(isActivePath("/en/gallery/interior/", "/en/gallery/interior", "en")).toBe(
      true,
    );
    expect(isActivePath("/en/gallery/", "/en/gallery/interior", "en")).toBe(true);
    expect(isActivePath("/en/homes/", "/en/gallery", "en")).toBe(false);
  });
});

describe("resolveStreamLinkHref", () => {
  it("builds mailto and tel links", () => {
    expect(
      resolveStreamLinkHref("email_link", { link: "leasing@onni.com" }),
    ).toBe("mailto:leasing@onni.com");
    expect(resolveStreamLinkHref("phone_link", { link: "604-555-0100" })).toBe(
      "tel:604-555-0100",
    );
  });

  it("prefers resolved_link over raw link", () => {
    expect(
      resolveStreamLinkHref("internal_page_link", {
        link: "/en/contact/",
        resolved_link: { url: "/en/contact/" },
      }),
    ).toBe("/en/contact/");
  });
});

describe("isExternalStreamLink", () => {
  it("detects external URLs", () => {
    expect(isExternalStreamLink("https://www.onni.com/")).toBe(true);
    expect(isExternalStreamLink("mailto:a@b.com")).toBe(true);
    expect(isExternalStreamLink("/documents/106/foo.pdf")).toBe(true);
    expect(isExternalStreamLink("/en/about-onni")).toBe(false);
  });
});
