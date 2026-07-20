/**
 * Locale-scoped not-found UI (client) — uses shared NotFoundPage.
 */

"use client";

import { NotFoundPage } from "@/components/NotFoundPage";
import { useParams } from "next/navigation";

/** App Router not-found for `/[locale]/*`. */
export default function NotFound() {
  const params = useParams<{ locale?: string }>();
  const locale = params?.locale ?? "en";
  return <NotFoundPage locale={locale} />;
}
