"use client";


/**
 * Browser QueryClientProvider for the App Router.
 */
import { useState, type ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { HeroVideoPreloadClient } from "@/components/layout/HeroVideoPreloadClient";
import { makeQueryClient } from "@/lib/query-client";

/** Provide TanStack Query to the client tree. */
export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <HeroVideoPreloadClient />
      {children}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
