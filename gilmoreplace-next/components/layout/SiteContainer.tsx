/**
 * Site layout: SiteContainer.
 */

import { cn } from "@/lib/utils";

interface SiteContainerProps {
  children: React.ReactNode;
  className?: string;
  fluid?: boolean;
}

export const siteContainerClass =
  "site-container mx-auto h-full w-full max-w-[85%] md:max-w-[80%]";
export const siteContainerFluidClass = "site-container site-container--fluid w-full";

/** Centered content width utility (site container class). */
export function SiteContainer({ children, className, fluid }: SiteContainerProps) {
  return (
    <div className={cn(fluid ? siteContainerFluidClass : siteContainerClass, className)}>
      {children}
    </div>
  );
}
