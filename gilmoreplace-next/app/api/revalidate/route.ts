/**
 * Next.js ISR revalidation webhook.
 * Auth: header ``X-Revalidation-Secret`` (preferred) or body/query ``secret``.
 * Called after CMS publish/unpublish to bust path/tag caches.
 */

import { revalidatePath, revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

function extractSecret(request: NextRequest, body: Record<string, unknown>): string {
  return (
    request.headers.get("X-Revalidation-Secret") ||
    (typeof body.secret === "string" ? body.secret : "") ||
    request.nextUrl.searchParams.get("secret") ||
    ""
  );
}

/** POST with secret + optional `{ path, paths, page_id, slug }`. */
export async function POST(request: NextRequest) {
  const expectedSecret = process.env.REVALIDATION_SECRET;
  const body = (await request.json().catch(() => ({}))) as Record<string, unknown>;
  const secret = extractSecret(request, body);

  if (!expectedSecret || secret !== expectedSecret) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 403 });
  }

  const paths = new Set<string>();
  if (typeof body.path === "string" && body.path) {
    paths.add(body.path.startsWith("/") ? body.path : `/${body.path}`);
  }
  if (Array.isArray(body.paths)) {
    for (const p of body.paths) {
      if (typeof p === "string" && p) {
        paths.add(p.startsWith("/") ? p : `/${p}`);
      }
    }
  }
  // Legacy: slug alone is ambiguous (no locale) — ignore for path busting.

  for (const path of paths) {
    revalidatePath(path);
  }

  const pageId = body.page_id;
  if (pageId !== undefined && pageId !== null) {
    revalidateTag(`page-${pageId}`);
  }

  revalidateTag("pages");
  revalidatePath("/", "layout");

  return NextResponse.json({
    revalidated: true,
    paths: [...paths],
  });
}
