/**
 * Site layout: Header.
 */

import Link from "next/link";
import {
  type LanguageRoot,
  type NavItem,
  type RootPageSettings,
  type SettingsResponse,
} from "@/lib/api/client";
import { FormAnchorLink } from "@/components/layout/FormAnchorLink";
import { HomeLogoLink } from "@/components/layout/HomeLogoLink";
import { PromoBoxTrigger } from "@/components/layout/PromoBoxContext";
import { MenuOpenButton } from "@/components/layout/SiteChrome";
import { wagtailUrlToNextPath } from "@/lib/urls";
import { isSameLocale, localeLabel } from "@/lib/i18n/config";

interface HeaderProps {
  nav: NavItem[];
  settings: SettingsResponse;
  locale: string;
  pageId?: number;
  rootPage?: RootPageSettings | null;
  languageRoots?: LanguageRoot[];
}

/** Site header: logo, nav, register CTA, menu toggle. */
export function Header({
  settings,
  locale,
  pageId,
  rootPage,
  languageRoots = [],
}: HeaderProps) {
  const contactHref = rootPage?.contact_page_url
    ? `${wagtailUrlToNextPath(rootPage.contact_page_url, locale)}#form`
    : null;

  return (
    <nav className="fixed">
      <div className="wrapper">
        <HomeLogoLink locale={locale} />

        <div className="mobile">
          {contactHref && <FormAnchorLink href={contactHref}>Register</FormAnchorLink>}
          <MenuOpenButton wrapperClassName="hamburger">
            <span />
            <span />
            <span />
          </MenuOpenButton>
        </div>

        <ul className="desktop">
          {rootPage?.header_promo_box && pageId === rootPage.header_promo_box.page_id ? (
            <li className="line header-pb">
              <PromoBoxTrigger className="info">
                {rootPage.header_promo_box.title}
              </PromoBoxTrigger>
            </li>
          ) : null}
          {rootPage?.penthouse_collections_url && (
            <li className="line header-pc">
              <Link
                href={wagtailUrlToNextPath(rootPage.penthouse_collections_url, locale)}
                className="info"
              >
                Penthouse Collection
              </Link>
            </li>
          )}
          {rootPage?.email && (
            <li className="line">
              <a target="_blank" rel="noopener noreferrer" href={`mailto:${rootPage.email}`} className="info">
                {rootPage.email}
              </a>
            </li>
          )}
          {rootPage?.phone && (
            <li className="line">
              <a target="_blank" rel="noopener noreferrer" href={`tel:${rootPage.phone}`} className="info">
                {rootPage.phone}
              </a>
            </li>
          )}
          <li className="locales">
            {languageRoots.map((lr, i) => (
              <span key={lr.language_code}>
                {i > 0 && <> | </>}
                <Link
                  href={wagtailUrlToNextPath(lr.url, locale)}
                  className={isSameLocale(locale, lr.language_code) ? "router-link-active active" : undefined}
                >
                  {lr.label || localeLabel(lr.language_code)}
                </Link>
              </span>
            ))}
          </li>
          {contactHref && (
            <li>
              <FormAnchorLink href={contactHref} className="btn purple">
                Register
              </FormAnchorLink>
            </li>
          )}
          <li>
            <MenuOpenButton className="btn-menu">Menu</MenuOpenButton>
          </li>
        </ul>
      </div>
    </nav>
  );
}
