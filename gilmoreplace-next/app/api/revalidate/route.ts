/**
 * Next.js ISR revalidation webhook (secret query param).
 * Called after CMS publish to bust path/tag caches.
 */

import { revalidatePath, revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

/** POST ?secret=… with optional `{ slug, page_id }` body. */
export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get("secret");
  const expectedSecret = process.env.REVALIDATION_SECRET;

  if (!expectedSecret || secret !== expectedSecret) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 403 });
  }

  const body = await request.json().catch(() => ({}));
  const { page_id, slug } = body;

  if (slug) {
    revalidatePath(`/${slug}`);
  }

  if (page_id) {
    revalidateTag(`page-${page_id}`);
  }

  revalidatePath("/", "layout");

  return NextResponse.json({ revalidated: true });
}
