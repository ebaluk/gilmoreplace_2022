"use client";

/**
 * Periodically refresh the RSC preview tree so Wagtail live preview updates appear.
 */

import { useRouter } from "next/navigation";
import { useEffect } from "react";

const POLL_MS = 2000;

export function PreviewLiveRefresh() {
  const router = useRouter();

  useEffect(() => {
    const id = window.setInterval(() => {
      router.refresh();
    }, POLL_MS);
    return () => window.clearInterval(id);
  }, [router]);

  return null;
}
