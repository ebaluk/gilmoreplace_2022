import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";

vi.mock("next/cache", () => ({
  revalidatePath: vi.fn(),
  revalidateTag: vi.fn(),
}));

describe("POST /api/revalidate", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    process.env.REVALIDATION_SECRET = "test-revalidate-secret";
  });

  it("rejects missing secret", async () => {
    const { POST } = await import("@/app/api/revalidate/route");
    const req = new NextRequest("http://localhost/api/revalidate", {
      method: "POST",
      body: JSON.stringify({ path: "/en/about" }),
      headers: { "content-type": "application/json" },
    });
    const res = await POST(req);
    expect(res.status).toBe(403);
  });

  it("accepts X-Revalidation-Secret header and revalidates path/tags", async () => {
    const { revalidatePath, revalidateTag } = await import("next/cache");
    const { POST } = await import("@/app/api/revalidate/route");
    const req = new NextRequest("http://localhost/api/revalidate", {
      method: "POST",
      body: JSON.stringify({ path: "/en/about", page_id: 42 }),
      headers: {
        "content-type": "application/json",
        "X-Revalidation-Secret": "test-revalidate-secret",
      },
    });
    const res = await POST(req);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.revalidated).toBe(true);
    expect(body.paths).toContain("/en/about");
    expect(revalidatePath).toHaveBeenCalledWith("/en/about");
    expect(revalidateTag).toHaveBeenCalledWith("page-42");
    expect(revalidateTag).toHaveBeenCalledWith("pages");
  });
});
