"use client";


/**
 * Site layout: SiteInteractions.
 */
import { usePathname } from "next/navigation";
import { useEffect, useLayoutEffect, useRef } from "react";
import { closeSiteMenu } from "@/components/layout/SiteChrome";

/** Client document-ready / path tracking for promo cadence. */
export function SiteInteractions() {
  const pathname = usePathname();
  const lastPathname = useRef<string | null>(null);

  // Close menu when route changes (client-nav is tracked in HeroVideoPreloadClient).
  useLayoutEffect(() => {
    if (lastPathname.current !== null && lastPathname.current !== pathname) {
      closeSiteMenu();
    }
    lastPathname.current = pathname;
  }, [pathname]);

  // Top banner should only collapse via menu state (slideUp/hide-nav).
  // Ensure we don't keep a stale scroll-down / stick state across navigations.
  useEffect(() => {
    document.body.classList.remove("scroll-down", "page-nav-fixed");
  }, [pathname]);

  // Stick page filter navbar below the top banner once it reaches the viewport top
  // (legacy site.js → body.page-nav-fixed → CSS top: 80px).
  useEffect(() => {
    const filterWrapper = document.getElementById("filterWrapper");
    if (!filterWrapper) return;

    let stickPoint = filterWrapper.offsetTop - 60;

    const handleScroll = () => {
      const elTop = filterWrapper.offsetTop;
      const offset = window.scrollY;
      const distance = elTop - offset;
      if (distance <= 0) {
        document.body.classList.add("page-nav-fixed");
      } else if (offset <= stickPoint) {
        document.body.classList.remove("page-nav-fixed");
      }
    };

    const handleResize = () => {
      stickPoint = filterWrapper.offsetTop - 60;
      handleScroll();
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleResize);
      document.body.classList.remove("page-nav-fixed");
    };
  }, [pathname]);

  // Always scroll to top on route change. In App Router, scroll restoration can
  // run after paint; schedule this after paint so it wins consistently.
  useEffect(() => {
    if (lastPathname.current === null) return;

    let raf1 = 0;
    let raf2 = 0;
    raf1 = window.requestAnimationFrame(() => {
      raf2 = window.requestAnimationFrame(() => {
        // Any sub-page that renders the filter navbar should land at #content.
        // `#filterWrapper` is rendered by `PageNavbar`.
        const shouldScrollToContent = Boolean(
          document.getElementById("filterWrapper"),
        );

        if (shouldScrollToContent) {
          const contentAnchor = document.getElementById("content");
          if (contentAnchor) {
            contentAnchor.scrollIntoView({ behavior: "auto", block: "start" });
            return;
          }
        }

        window.scrollTo({ top: 0, left: 0, behavior: "auto" });
      });
    });

    return () => {
      window.cancelAnimationFrame(raf1);
      window.cancelAnimationFrame(raf2);
    };
  }, [pathname]);

  return null;
}
