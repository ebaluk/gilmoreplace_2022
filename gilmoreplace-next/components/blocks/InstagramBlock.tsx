/**
 * Stream-field block UI for `InstagramBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";

interface InstagramValue {
  title?: string;
  items?: { image_url: string; link: string; caption?: string }[];
  theme?: { id: number; css_class: string | null } | null;
}

/** Wagtail Instagram feed strip. */
export function InstagramBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as InstagramValue;
  const { title, items = [], theme } = value;

  if (!items.length) return null;

  return (
    <article
      className={`instagram-block${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      {title && <h2 className="title h1 text-center">{title}</h2>}
      <div className="instagram-grid">
        {items.map((item, i) => (
          <a
            key={i}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="instagram-item"
            style={{ backgroundImage: `url(${item.image_url})` }}
          >
            {item.caption && <span className="caption">{item.caption}</span>}
          </a>
        ))}
      </div>
    </article>
  );
}
