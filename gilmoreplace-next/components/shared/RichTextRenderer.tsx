"use client";


/**
 * Shared UI: RichTextRenderer.
 */
import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface RichTextRendererProps {
  html: string;
  className?: string;
}

/** Dangerously render Wagtail rich text HTML with safe defaults. */
export function RichTextRenderer({ html, className }: RichTextRendererProps) {
  const processed = useMemo(() => {
    if (!html) return "";
    if (typeof DOMParser === "undefined") return html;
    const doc = new DOMParser().parseFromString(html, "text/html");

    doc.querySelectorAll("[data-block-key]").forEach((el) => {
      el.removeAttribute("data-block-key");
    });

    doc.querySelectorAll("a[href]").forEach((el) => {
      const href = el.getAttribute("href") || "";
      if (href.startsWith("mailto:") || href.startsWith("tel:")) {
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "noopener noreferrer");
      }
    });

    return doc.body.innerHTML;
  }, [html]);

  if (!html) return null;

  return (
    <div
      className={cn("prose max-w-none", className)}
      dangerouslySetInnerHTML={{ __html: processed }}
    />
  );
}
