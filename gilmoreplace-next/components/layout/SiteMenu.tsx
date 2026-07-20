/**
 * Site layout: SiteMenu.
 */

import { type LanguageRoot, type NavItem, type RootPageSettings } from "@/lib/api/client";
import { type WagtailPage } from "@/types/page";
import { MenuCloseButton, MenuNavLink } from "@/components/layout/SiteChrome";
import { wagtailUrlToNextPath } from "@/lib/urls";
import { isSameLocale, localeLabel } from "@/lib/i18n/config";

interface SiteMenuProps {
  nav: NavItem[];
  page: WagtailPage;
  locale: string;
  rootPage?: RootPageSettings | null;
  languageRoots?: LanguageRoot[];
}

function isNavActive(pageUrl: string, itemUrl: string, locale: string): boolean {
  const pagePath = wagtailUrlToNextPath(pageUrl, locale);
  const itemPath = wagtailUrlToNextPath(itemUrl, locale);
  return pagePath === itemPath || pagePath.startsWith(`${itemPath}/`);
}

function getActiveTopNavItem(
  nav: NavItem[],
  pageUrl: string,
  locale: string
): NavItem | null {
  for (const item of nav) {
    if (isNavActive(pageUrl, item.url, locale)) {
      return item;
    }
    for (const child of item.children) {
      if (isNavActive(pageUrl, child.url, locale)) {
        return item;
      }
    }
  }
  return null;
}

/** Full-screen mobile/desktop menu overlay. */
export function SiteMenu({
  nav,
  page,
  locale,
  rootPage,
  languageRoots = [],
}: SiteMenuProps) {
  const activeTop = getActiveTopNavItem(nav, page.url, locale);
  const showChildren = Boolean(
    activeTop?.show_navbar && activeTop.children.length > 0
  );

  return (
    <div className="menu">
      <MenuNavLink href={`/${locale}`} className="logo" aria-current="page">
        <img src="/images/logo-bordered.svg" alt="Gilmore" className="desktop" />
        <img src="/images/logo.svg" alt="Gilmore" className="mobile" />
      </MenuNavLink>

      <ul className="routes">
        {nav.map((item, index) => {
          const active = isNavActive(page.url, item.url, locale);
          return (
            <li key={item.id}>
              <MenuNavLink
                href={wagtailUrlToNextPath(item.url, locale)}
                className={`route${active ? " router-link-exact-active router-link-active" : ""}`}
              >
                <span>{String(index + 1).padStart(2, "0")}</span>
                {item.title}
              </MenuNavLink>
            </li>
          );
        })}
        {showChildren && activeTop && (
          <li>
            <ul className="menu-boxes active">
              {activeTop.children.map((child) => {
                const childActive =
                  page.content_page_id === child.id ||
                  isNavActive(page.url, child.url, locale);
                return (
                  <li
                    key={child.id}
                    className={`section-box${childActive ? " active" : ""}`}
                  >
                    <MenuNavLink
                      href={`${wagtailUrlToNextPath(child.url, locale)}#content`}
                      className={
                        childActive
                          ? "router-link-exact-active router-link-active"
                          : undefined
                      }
                    >
                      {child.title}
                    </MenuNavLink>
                  </li>
                );
              })}
            </ul>
          </li>
        )}
      </ul>

      <div className="footer">
        <div className="links desktop">
          {rootPage?.phone && (
            <a target="_blank" rel="noopener noreferrer" href={`tel:${rootPage.phone}`}>
              {rootPage.phone}
            </a>
          )}
          {rootPage?.email && (
            <>
              {rootPage.phone && <> &nbsp; | &nbsp; </>}
              <a target="_blank" rel="noopener noreferrer" href={`mailto:${rootPage.email}`}>
                {rootPage.email}
              </a>
            </>
          )}
        </div>

        <div className="right">
          {rootPage?.footer_social_links?.length ? (
            <ul className="social-media">
              {rootPage.footer_social_links.map((social, i) => (
                <li key={i}>
                  <a
                    href={social.link}
                    target={social.new_window ? "_blank" : undefined}
                    rel={social.new_window ? "noopener noreferrer" : undefined}
                    title={social.title}
                  >
                    <i className={`fa ${social.fontawesome_icon} fa-2x`} aria-hidden="true" />
                  </a>
                </li>
              ))}
            </ul>
          ) : null}
          <br />
          <a href="https://www.onni.com/" target="_blank" rel="noopener noreferrer">
            <img src="/images/onni-logo.svg" alt="Onni Group" className="logo-onni" />
          </a>

          <div className="locales">
            {languageRoots.map((lr, i) => (
              <span key={lr.language_code}>
                {i > 0 && <> | </>}
                <MenuNavLink
                  href={wagtailUrlToNextPath(lr.url, locale)}
                  className={isSameLocale(locale, lr.language_code) ? "active" : undefined}
                >
                  {lr.label || localeLabel(lr.language_code)}
                </MenuNavLink>
              </span>
            ))}
          </div>

          <div className="links mobile">
            {rootPage?.phone && (
              <a target="_blank" rel="noopener noreferrer" href={`tel:${rootPage.phone}`}>
                {rootPage.phone}
              </a>
            )}
            {rootPage?.email && (
              <>
                {rootPage.phone && <br />}
                <a target="_blank" rel="noopener noreferrer" href={`mailto:${rootPage.email}`}>
                  {rootPage.email}
                </a>
              </>
            )}
          </div>

          <br />
          {rootPage?.footer_legal && (
            <div
              className="disclaimer"
              dangerouslySetInnerHTML={{ __html: rootPage.footer_legal }}
            />
          )}
          <a
            href="https://www.onni.com/privacy/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ textTransform: "none", marginTop: 10, display: "block" }}
          >
            <p className="disclaimer">Privacy Policy</p>
          </a>
        </div>
      </div>

      <MenuCloseButton className="close" />
    </div>
  );
}
