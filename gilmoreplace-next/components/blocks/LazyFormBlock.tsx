"use client";


/**
 * Stream-field block UI for `LazyFormBlock`.
 */
import dynamic from "next/dynamic";
import { type StreamFieldBlock } from "@/types/page";

const FormBlock = dynamic(
  () => import("@/components/blocks/FormBlock").then((m) => m.FormBlock),
  { ssr: false }
);

/** Lazy-load FormBlock when the form id is present. */
export function LazyFormBlock({
  block,
  locale,
}: {
  block: StreamFieldBlock;
  locale: string;
}) {
  return <FormBlock block={block} locale={locale} />;
}
