"use client";


/**
 * Stream-field block UI for `SiteMapBlock`.
 */
import type { StreamFieldBlock } from "@/types/page";

interface SiteMapLink {
  id: string;
  type: string;
  value: {
    title?: string;
    link?: string;
    children?: SiteMapLink[];
  };
}

interface SiteMapValue {
  title?: string;
  items?: SiteMapLink[];
  theme?: { id: number; css_class: string | null } | null;
}

/** Wagtail "site_map" interactive map wrapper. */
export function SiteMapBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as SiteMapValue;
  const { title, items = [], theme } = value;

  if (!items.length) return null;

  return (
    <article
      className={`site-map-block${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      {title && <h2 className="title h1">{title}</h2>}
      <ul className="site-map-list">
        {items.map((item) => (
          <SiteMapItem key={item.id} item={item} />
        ))}
      </ul>
    </article>
  );
}

function SiteMapItem({ item }: { item: SiteMapLink }) {
  return (
    <li>
      {item.value.link ? (
        <a href={item.value.link}>{item.value.title}</a>
      ) : (
        <span>{item.value.title}</span>
      )}
      {item.value.children && item.value.children.length > 0 && (
        <ul>
          {item.value.children.map((child) => (
            <SiteMapItem key={child.id} item={child} />
          ))}
        </ul>
      )}
    </li>
  );
}
