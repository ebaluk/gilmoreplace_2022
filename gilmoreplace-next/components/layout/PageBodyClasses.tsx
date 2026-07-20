"use client";


/**
 * Site layout: PageBodyClasses.
 */
import { useEffect } from "react";

const MANAGED_PREFIXES = ["color-theme-", "body-"];

function parseBodyClasses(className: string): string[] {
  return className.split(/\s+/).filter((c) =>
    MANAGED_PREFIXES.some((prefix) => c.startsWith(prefix))
  );
}

/** Sync body.color-theme-* classes with the current page. */
export function PageBodyClasses({ className }: { className: string }) {
  useEffect(() => {
    const classes = parseBodyClasses(className);
    classes.forEach((c) => document.body.classList.add(c));
    return () => {
      classes.forEach((c) => document.body.classList.remove(c));
    };
  }, [className]);

  return null;
}
