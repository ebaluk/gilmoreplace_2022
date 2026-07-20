import { afterEach, describe, expect, it } from "vitest";
import { cn, formatImageUrl } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", false && "bar", "baz")).toBe("foo baz");
  });
});

describe("formatImageUrl", () => {
  it("returns absolute URLs unchanged", () => {
    expect(formatImageUrl("https://cdn.example.com/a.jpg")).toBe(
      "https://cdn.example.com/a.jpg",
    );
  });

  it("returns root-relative paths unchanged", () => {
    expect(formatImageUrl("/media_files/images/test.jpg")).toBe(
      "/media_files/images/test.jpg",
    );
  });

  it("returns empty string for missing URLs", () => {
    expect(formatImageUrl(null)).toBe("");
  });
});
