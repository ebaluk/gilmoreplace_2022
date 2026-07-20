"use client";

/**
 * Shared UI: RichTextRenderer.
 * Processes Wagtail rich text identically on server and client (no DOMParser)
 * so hydration matches.
 */
import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface RichTextRendererProps {
  html: string;
  className?: string;
}

/** Strip Draftail keys and ensure mailto/tel links open safely. */
export function processRichTextHtml(html: string): string {
  if (!html) return "";

  let out = html.replace(/\s*data-block-key=(["'])[^"']*\1/gi, "");

  out = out.replace(
    /<a(\s[^>]*?)href=(["'])(mailto:|tel:)([^"']*)\2([^>]*)>/gi,
    (match, before: string, q: string, scheme: string, rest: string, after: string) => {
      const attrs = `${before}${after}`;
      if (/\btarget\s*=/i.test(attrs)) return match;
      return `<a${before}href=${q}${scheme}${rest}${q}${after} target="_blank" rel="noopener noreferrer">`;
    },
  );

  return out;
}

/** Dangerously render Wagtail rich text HTML with safe defaults. */
export function RichTextRenderer({ html, className }: RichTextRendererProps) {
  const processed = useMemo(() => processRichTextHtml(html), [html]);

  if (!html) return null;

  return (
    <div
      className={cn("prose max-w-none", className)}
      dangerouslySetInnerHTML={{ __html: processed }}
    />
  );
}
