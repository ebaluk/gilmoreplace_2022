"use client";


/**
 * Site layout: SiteChrome.
 */
import Link from "next/link";
import { type ComponentProps, type MouseEvent, type ReactNode } from "react";

/** Add body classes that slide the full-site menu open. */
export function openSiteMenu() {
  document.body.classList.add("slideUp", "hide-nav");
}

/** Remove slide-up menu body classes. */
export function closeSiteMenu() {
  document.body.classList.remove("slideUp", "hide-nav");
}

/** Next Link that closes the site menu on click. */
export function MenuNavLink({
  href,
  className,
  children,
  onClick,
  ...props
}: ComponentProps<typeof Link>) {
  return (
    <Link
      href={href}
      className={className}
      {...props}
      onClick={(e) => {
        closeSiteMenu();
        onClick?.(e);
      }}
    >
      {children}
    </Link>
  );
}

/** Smooth-scroll one viewport past the hero. */
export function scrollPastHero() {
  window.scrollTo({ top: window.innerHeight, behavior: "smooth" });
}

/** Button that opens the full-site slide-up menu. */
export function MenuOpenButton({
  children,
  className,
  wrapperClassName,
}: {
  children: ReactNode;
  className?: string;
  wrapperClassName?: string;
}) {
  const onClick = (e: MouseEvent) => {
    e.preventDefault();
    openSiteMenu();
  };

  if (className === undefined) {
    return (
      <div
        className={wrapperClassName}
        onClick={onClick}
        onKeyDown={(e) => e.key === "Enter" && onClick(e as unknown as MouseEvent)}
        role="button"
        tabIndex={0}
      >
        {children}
      </div>
    );
  }

  return (
    <a href="#" className={className} onClick={onClick}>
      {children}
    </a>
  );
}

/** Control that closes the full-site slide-up menu. */
export function MenuCloseButton({ className }: { className?: string }) {
  return (
    <div
      className={className}
      role="button"
      tabIndex={0}
      aria-label="Close menu"
      onClick={(e) => {
        e.preventDefault();
        closeSiteMenu();
      }}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          closeSiteMenu();
        }
      }}
    />
  );
}

/** Hero scroll cue that scrolls past the fold on click. */
export function ScrollDownButton({
  src,
  alt = "",
  className,
}: {
  src: string;
  alt?: string;
  className?: string;
}) {
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      role="button"
      tabIndex={0}
      onClick={(e) => {
        e.preventDefault();
        scrollPastHero();
      }}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          scrollPastHero();
        }
      }}
    />
  );
}
