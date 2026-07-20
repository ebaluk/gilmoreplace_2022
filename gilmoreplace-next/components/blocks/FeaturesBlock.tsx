"use client";


/**
 * Stream-field block UI for `FeaturesBlock`.
 */
import { useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { RelatedLinks } from "@/components/shared/RelatedLinks";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface FeatureItemData {
  title?: string;
  items?: { text: string; force_new_column?: boolean }[];
}

interface FeaturesValue {
  title?: string;
  title_2?: string;
  features?: (FeatureItemData | { type?: string; id?: string; value?: FeatureItemData })[];
  theme?: { id: number; css_class: string | null } | null;
  new_links?: {
    align?: string;
    description?: string;
    links?: {
      type: string;
      value: {
        title?: string;
        link_type?: string;
        new_window?: boolean;
        resolved_link?: { url: string } | null;
      };
    }[];
  };
}

function normalizeFeature(
  feature: FeaturesValue["features"] extends (infer T)[] | undefined ? T : never,
  index: number,
): FeatureItemData & { id: string } {
  if (feature && "value" in feature && feature.value) {
    return { id: feature.id ?? String(index), ...feature.value };
  }
  const flat = feature as FeatureItemData;
  return { id: String(index), title: flat.title, items: flat.items };
}

/** Wagtail "features" block — accordion feature lists + download CTAs. */
export function FeaturesBlock({
  block,
  locale,
}: {
  block: StreamFieldBlock;
  locale: string;
}) {
  const value = block.value as unknown as FeaturesValue;
  const { title, title_2, features = [], theme, new_links } = value;

  const normalized = features.map(normalizeFeature).filter((f) => f.title);
  const [openIds, setOpenIds] = useState<Set<string>>(() => new Set());

  const toggleFeature = (id: string) => {
    setOpenIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <article
      className={`features-block${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
    >
      <div className={cn("flexbox", siteContainerClass)}>
        <div className="flex-item">
          {title && (
            <h2 className="title h1">
              {title}
              {title_2 && (
                <>
                  <br />
                  <span>{title_2.split("\n").map((line, i) => (
                    <span key={i}>
                      {i > 0 && <br />}
                      {line}
                    </span>
                  ))}</span>
                </>
              )}
            </h2>
          )}
          {new_links?.links?.length ? (
            <RelatedLinks links={new_links} locale={locale} />
          ) : null}
        </div>

        <div className="accordion-container flex-item">
          {normalized.map((feature) => (
            <FeatureAccordionItem
              key={feature.id}
              feature={feature}
              open={openIds.has(feature.id)}
              onToggle={() => toggleFeature(feature.id)}
            />
          ))}
        </div>
      </div>
    </article>
  );
}

function FeatureAccordionItem({
  feature,
  open,
  onToggle,
}: {
  feature: FeatureItemData & { id: string };
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="accordion">
      <div
        className="header"
        role="tab"
        aria-expanded={open ? "true" : "false"}
        onClick={onToggle}
      >
        <h2 className="subhead white underline">{feature.title}</h2>
        <button
          type="button"
          className="btn-plus"
          aria-label={open ? "Collapse section" : "Expand section"}
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
        >
          <svg width="16" height="16" viewBox="0 0 16 16">
            <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
              <g stroke="#FFFFFF" strokeWidth="2">
                <path d="M8,0 L8,16" />
                <path d="M16,8 L0,8" />
              </g>
            </g>
          </svg>
        </button>
      </div>
      <div
        className={`accordion-panel${open ? " is-open" : ""}`}
        role="tabpanel"
        aria-hidden={!open}
      >
        <div className="accordion-panel-inner">
          <div className="columns">
            {(feature.items || []).map((item, i) => (
              <div key={i} className="col rich-text">
                <RichTextRenderer html={item.text} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
