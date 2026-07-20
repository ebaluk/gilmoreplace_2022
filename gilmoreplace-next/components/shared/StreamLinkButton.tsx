/**
 * Shared UI: StreamLinkButton.
 */

import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { formatImageUrl } from "@/lib/utils";
import {
  isExternalStreamLink,
  resolveStreamLinkHref,
  wagtailUrlToNextPath,
} from "@/lib/urls";

export interface StreamLinkItem {
  type: string;
  value: {
    title?: string;
    link_type?: string;
    link?: string | number;
    new_window?: boolean;
    resolved_link?: { url?: string; id?: number; title?: string; submit_url?: string } | null;
  };
}

function linkVariant(linkType: string): "gold" | "reverse" | "link" | "default" {
  if (linkType === "gold") return "gold";
  if (linkType === "button") return "default"; // white .btn — not purple
  if (linkType === "reverse") return "reverse";
  return "link";
}

/** Render a CMS stream link as Button, Link, or plain anchor by link_type. */
export function StreamLinkButton({
  link,
  locale,
  className,
}: {
  link: StreamLinkItem;
  locale: string;
  className?: string;
}) {
  const { title, link_type = "link", new_window } = link.value;
  const rawUrl = resolveStreamLinkHref(link.type, link.value);
  if (!title || !rawUrl) return null;

  const isExternal = isExternalStreamLink(rawUrl);
  const isMedia = rawUrl.startsWith("/media");
  const href = isMedia ? formatImageUrl(rawUrl) : rawUrl;
  const target = new_window || isExternal || isMedia ? "_blank" : undefined;
  const rel = target ? "noopener noreferrer" : undefined;
  const isButton =
    link_type === "button" || link_type === "gold" || link_type === "reverse";

  if (isButton) {
    const variant = linkVariant(link_type);
    if (isExternal || isMedia) {
      return (
        <Button asChild variant={variant} className={className}>
          <a href={href} target={target} rel={rel}>
            {title}
          </a>
        </Button>
      );
    }
    return (
      <Button asChild variant={variant} className={className}>
        <Link href={wagtailUrlToNextPath(href, locale)}>{title}</Link>
      </Button>
    );
  }

  if (isExternal || isMedia) {
    return (
      <a href={href} target={target} rel={rel} className={cn("link", className)}>
        {title}
      </a>
    );
  }

  return (
    <Link href={wagtailUrlToNextPath(href, locale)} className={cn("link", className)}>
      {title}
    </Link>
  );
}

export { buttonVariants };
