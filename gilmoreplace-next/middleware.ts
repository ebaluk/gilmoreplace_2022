/**
 * Next.js middleware: redirect `/` to a negotiated locale; pass through other routes.
 */

import { NextRequest, NextResponse } from "next/server";
import { negotiateLocale } from "@/lib/i18n/negotiate";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname === "/") {
    const locale = negotiateLocale(request.headers.get("accept-language"));
    const url = request.nextUrl.clone();
    url.pathname = `/${locale}`;
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|woff2?|ico)$).*)",
  ],
};
