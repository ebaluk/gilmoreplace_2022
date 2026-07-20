/**
 * Stream-field block UI for `TextBlock`.
 */

import { type StreamFieldBlock, type ImageData } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { StreamLinkButton } from "@/components/shared/StreamLinkButton";
import { formatImageUrl } from "@/lib/utils";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";
import { DayNightTimeSlider } from "@/components/blocks/DayNightTimeSlider";

interface TextBlockValue {
  title?: string;
  title_2?: string;
  title_type?: "default" | "subhead" | "gold";
  layout?: "left" | "right" | "whole";
  larger?: boolean;
  spacing?: boolean;
  more_spacing?: boolean;
  bottom?: boolean;
  theme?: { id: number; css_class: string | null } | null;
  resolved_image?: ImageData | null;
  resolved_night_time_image?: ImageData | null;
  text_align?: string;
  text?: string;
  new_links?: {
    align?: string;
    description?: string;
    links?: LinkItem[];
  };
}

interface LinkItem {
  type: string;
  value: {
    title?: string;
    link_type?: string;
    link?: string;
    new_window?: boolean;
    resolved_link?: { id: number; title: string; url: string } | null;
  };
}

/** Wagtail "paragraph" text/image layout block. */
export function TextBlock({ block, locale }: { block: StreamFieldBlock; locale: string }) {
  const value = block.value as unknown as TextBlockValue;
  const {
    title,
    title_2,
    title_type = "default",
    layout = "whole",
    larger,
    spacing,
    more_spacing,
    bottom,
    theme,
    resolved_image,
    resolved_night_time_image,
    text_align,
    text,
    new_links,
  } = value;

  const hasImage = resolved_image;
  const showFlexLayout = layout !== "whole" && hasImage;

  const renderTitle = () => {
    if (!title && !title_2) return null;
    const titleClass =
      title_type === "subhead"
        ? "subhead"
        : `title h1${title_type === "gold" ? " gold" : ""}`;
    return (
      <h2 className={titleClass}>
        {title}
        {title && title_2 && <br />}
        {title_2 && <span className="whitespace-pre-line">{title_2}</span>}
      </h2>
    );
  };

  const renderLinks = () => {
    if (!new_links?.links?.length) return null;
    return (
      <div className={`related-links uppercase${new_links.align ? ` ${new_links.align}` : ""}`}>
        {new_links.description && <p>{new_links.description}</p>}
        <div className="links">
          {new_links.links.map((link, i) => {
            if (link.type === "onni_link") {
              const { title, new_window } = link.value;
              return (
                <a
                  key={`onni-${i}`}
                  href="https://www.onni.com/"
                  target={new_window ? "_blank" : undefined}
                  rel={new_window ? "noopener noreferrer" : undefined}
                  className="onni-link"
                  title={title}
                >
                  <img src="/images/onni-logo.svg" alt={title || "ONNI"} />
                </a>
              );
            }
            return (
              <StreamLinkButton
                key={`${link.type}-${link.value?.title ?? "link"}-${i}`}
                link={link}
                locale={locale}
              />
            );
          })}
        </div>
      </div>
    );
  };

  const renderContent = () => (
    <>
      {renderTitle()}
      <div
        className={`body-text${text_align ? ` text-${text_align}` : ""}${larger ? " larger" : ""}${spacing ? " spacing" : ""}${more_spacing ? " more-spacing" : ""}`}
      >
        <RichTextRenderer html={text || ""} />
        {renderLinks()}
      </div>
    </>
  );

  const renderImageBlock = () => {
    if (!resolved_image) return null;
    if (resolved_night_time_image) {
      return (
        <DayNightTimeSlider
          daySrc={resolved_image.url}
          dayAlt={resolved_image.alt}
          nightSrc={resolved_night_time_image.url}
          nightAlt={resolved_night_time_image.alt}
        />
      );
    }
    return (
      <img
        src={formatImageUrl(resolved_image.url)}
        alt={resolved_image.alt}
      />
    );
  };

  const themeId = theme?.id;
  const themeClass = theme?.css_class;

  return (
    <article
      className={cn(
        "text-block site-container layout-" + layout,
        themeId ? `themed-${themeId}` : "",
        themeClass || ""
      )}
    >
      <div className={`content${bottom ? " bottom" : ""}`}>
        {showFlexLayout ? (
          <div className={`flexbox${layout === "left" ? " orderChanged" : ""}`}>
            <div className="flex-item image">{renderImageBlock()}</div>
            <div className="flex-item">{renderContent()}</div>
          </div>
        ) : (
          renderContent()
        )}
      </div>
    </article>
  );
}
