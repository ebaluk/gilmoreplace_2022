/**
 * Stream-field block UI for `InfoBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface InfoItemData {
  title?: string;
  text?: string;
}

interface InfoValue {
  title?: string;
  title_2?: string;
  items?: (InfoItemData | { type?: string; id?: string; value?: InfoItemData })[];
  theme?: { id: number; css_class: string | null } | null;
}

function normalizeInfoItem(
  item: InfoValue["items"] extends (infer T)[] | undefined ? T : never,
): InfoItemData {
  if (item && "value" in item && item.value) {
    return item.value;
  }
  return item as InfoItemData;
}

/** Wagtail "info" blocks list. */
export function InfoBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as InfoValue;
  const { title, title_2, items = [], theme } = value;
  const normalized = items.map(normalizeInfoItem).filter((item) => item.title || item.text);

  return (
    <article
      className={`info-blocks${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      <img
        src="/images/svgs/info-block-pattern.svg"
        alt=""
        className="pattern"
        aria-hidden="true"
      />
      <div className={cn("blocks", siteContainerClass)}>
        {(title || title_2) && (
          <div className="block stat">
            {title && <h1>{title}</h1>}
            {title_2 && (
              <h3 className="subhead">
                {title_2.split("\n").map((line, i) => (
                  <span key={i}>
                    {i > 0 && <br />}
                    {line}
                  </span>
                ))}
              </h3>
            )}
          </div>
        )}
        {normalized.map((item, i) => (
          <div key={i} className="block details">
            {item.title && <h3 className="subhead white underline">{item.title}</h3>}
            {item.text && <RichTextRenderer html={item.text} />}
          </div>
        ))}
      </div>
    </article>
  );
}
