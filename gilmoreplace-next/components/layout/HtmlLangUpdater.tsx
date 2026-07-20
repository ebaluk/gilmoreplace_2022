"use client";


/**
 * Site layout: HtmlLangUpdater.
 */
import { useEffect } from "react";
import { htmlLangFromRoute } from "@/lib/i18n/config";

/** Client effect to set documentElement.lang from locale. */
export function HtmlLangUpdater({ locale }: { locale: string }) {
  useEffect(() => {
    document.documentElement.lang = htmlLangFromRoute(locale);
  }, [locale]);

  return null;
}

