/**
 * Stream-field block UI for `RawHtmlBlock`.
 *
 * Trust policy: HTML is authored only by CMS editors (Wagtail admin).
 * We do not sanitize here — treat raw_html as privileged CMS content.
 */

import type { StreamFieldBlock } from "@/types/page";

interface RawHtmlValue {
  html?: string;
}

/** Wagtail raw HTML passthrough (CMS-trusted). */
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
