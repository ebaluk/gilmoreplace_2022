import { describe, expect, it, vi } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { prefetchPageData } from "@/lib/api/prefetch-page";
import { queryKeys } from "@/lib/api/query-keys";

describe("queryKeys", () => {
  it("builds stable page keys", () => {
    expect(queryKeys.pages.bySlug("en", "penthouses")).toEqual([
      "pages",
      "en",
      "penthouses",
    ]);
  });

  it("builds navigation and settings keys", () => {
    expect(queryKeys.navigation("sc")).toEqual(["navigation", "sc"]);
    expect(queryKeys.settings("tc")).toEqual(["settings", "tc"]);
  });
});

describe("prefetchPageData", () => {
  it("returns found when page fetch succeeds", async () => {
    const queryClient = new QueryClient();
    const prefetchQuery = vi
      .spyOn(queryClient, "prefetchQuery")
      .mockResolvedValue(undefined);
    const fetchQuery = vi
      .spyOn(queryClient, "fetchQuery")
      .mockResolvedValue({ id: 1 });

    const result = await prefetchPageData(queryClient, "en", "penthouses");

    expect(result).toEqual({ found: true });
    expect(prefetchQuery).toHaveBeenCalledTimes(2);
    expect(fetchQuery).toHaveBeenCalledTimes(1);
    expect(fetchQuery.mock.calls[0][0].queryKey).toEqual(
      queryKeys.pages.bySlug("en", "penthouses"),
    );
  });

  it("returns not found when page fetch fails", async () => {
    const queryClient = new QueryClient();
    vi.spyOn(queryClient, "prefetchQuery").mockResolvedValue(undefined);
    vi.spyOn(queryClient, "fetchQuery").mockRejectedValue(
      new Error("API error: 404"),
    );

    const result = await prefetchPageData(queryClient, "en", "missing-page");

    expect(result).toEqual({ found: false });
  });
});
