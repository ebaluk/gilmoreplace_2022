/**
 * Stream-field block UI for `HashBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";

interface HashValue {
  hash?: string;
}

/** Wagtail "hash" in-page anchor. */
export function HashBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as HashValue;
  if (!value.hash) return null;

  return <div id={value.hash.replace(/^#/, "")} className="hash-anchor" />;
}
