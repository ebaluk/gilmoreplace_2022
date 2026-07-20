/**
 * Stream-field block UI for `RawHtmlBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";

interface RawHtmlValue {
  html?: string;
}

/** Wagtail raw HTML passthrough. */
export function RawHtmlBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as RawHtmlValue;
  if (!value.html) return null;

  return (
    <div
      className="raw-html-block"
      dangerouslySetInnerHTML={{ __html: value.html }}
    />
  );
}
