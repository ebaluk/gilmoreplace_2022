/**
 * Stream-field block UI for `ContactBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { SiteContainer } from "@/components/layout/SiteContainer";

interface ContactItemValue {
  title?: string;
  text?: string;
}

interface ContactItem {
  id?: string;
  type?: string;
  value?: ContactItemValue;
  title?: string;
  text?: string;
}

interface ContactValue {
  items?: ContactItem[];
  theme?: { id: number; css_class: string | null } | null;
}

function getContactItemFields(item: ContactItem): ContactItemValue | null {
  if (item.value?.title || item.value?.text) {
    return item.value;
  }
  if (item.title || item.text) {
    return { title: item.title, text: item.text };
  }
  return null;
}

/** Wagtail "contact" info columns. */
export function ContactBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as ContactValue;
  const { items = [], theme } = value;

  return (
    <article
      className={`contact-block${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      <SiteContainer>
        <div className="content">
          {items.map((item, index) => {
            const fields = getContactItemFields(item);
            if (!fields) return null;
            return (
              <div key={item.id || String(index)} className="block details">
                {fields.title && (
                  <h3 className="subhead">{fields.title}</h3>
                )}
                {fields.text && (
                  <RichTextRenderer html={fields.text} />
                )}
              </div>
            );
          })}
        </div>
      </SiteContainer>
    </article>
  );
}
