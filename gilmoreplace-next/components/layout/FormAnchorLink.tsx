"use client";


/**
 * Site layout: FormAnchorLink.
 */
import Link from "next/link";
import { type ReactNode } from "react";

/** Header Register link that scrolls/opens the contact form. */
export function FormAnchorLink({
  href,
  children,
  className,
}: {
  href: string;
  children: ReactNode;
  className?: string;
}) {
  const scrollToForm = () => {
    document.getElementById("form")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <Link
      href={href}
      className={className}
      scroll={false}
      onClick={() => {
        if (href.includes("#form")) {
          queueMicrotask(scrollToForm);
        }
      }}
    >
      {children}
    </Link>
  );
}
