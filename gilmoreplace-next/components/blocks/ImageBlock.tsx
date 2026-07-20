/**
 * Stream-field block UI for `ImageBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";

interface ResolvedImage {
  id: number;
  url: string;
  alt: string;
  width: number;
  height: number;
}

interface ImageValue {
  image?: number | ResolvedImage;
  resolved_image?: ResolvedImage;
  theme?: { id: number; css_class: string | null } | null;
}

function getImage(value: ImageValue): ResolvedImage | null {
  if (value.resolved_image?.url) return value.resolved_image;
  if (value.image && typeof value.image === "object" && value.image.url) {
    return value.image;
  }
  return null;
}

/** Wagtail "image" block. */
export function ImageBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as ImageValue;
  const { theme } = value;
  const image = getImage(value);

  if (!image) return null;

  return (
    <article
      className={`image-block${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      <img
        src={formatImageUrl(image.url)}
        alt={image.alt || ""}
        loading="lazy"
      />
    </article>
  );
}
