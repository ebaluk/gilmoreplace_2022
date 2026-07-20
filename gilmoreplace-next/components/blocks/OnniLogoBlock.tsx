/**
 * Stream-field block UI for `OnniLogoBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";

interface OnniLogoValue {
  logo?: { id: number; url: string; alt: string; width: number; height: number };
  link?: string;
}

/** Wagtail Onni logo block. */
export function OnniLogoBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as OnniLogoValue;
  const { logo, link } = value;

  if (!logo) return null;

  const img = (
    <img
      src={formatImageUrl(logo.url)}
      alt={logo.alt || ""}
      width={logo.width}
      height={logo.height}
    />
  );

  return (
    <div className="onni-logo-block">
      {link ? (
        <a href={link} target="_blank" rel="noopener noreferrer">
          {img}
        </a>
      ) : (
        img
      )}
    </div>
  );
}
