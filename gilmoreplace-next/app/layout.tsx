/**
 * Root layout: global CSS, Font Awesome, theme CSS injection, React Query provider.
 */

import type { Metadata } from "next";
import "@/styles/nunito-sans.css";
import "@/styles/fonts.css";
import "@/styles/globals.css";
import "@/styles/site.css";
import "@/styles/promobox.css";
import "@/styles/gallery-dialog.css";
import "@/styles/gallery-tile.css";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/effect-fade";
import { ThemeStyles } from "@/components/layout/ThemeStyles";
import { QueryProvider } from "@/components/providers/QueryProvider";

export const metadata: Metadata = {
  title: "Gilmore Place",
  description: "Gilmore Place - Luxury Residences in Burnaby, BC",
};

/** HTML shell shared by all routes. */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        />
        <ThemeStyles />
      </head>
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
