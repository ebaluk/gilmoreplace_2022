/**
 * Assembles chrome (header/hero/stream/footer) for a hydrated Wagtail page.
 */

import { type WagtailPage } from "@/types/page";
import { type NavItem, type SettingsResponse } from "@/lib/api/client";
import { Header } from "@/components/layout/Header";
import { Hero } from "@/components/layout/Hero";
import { MetaTags } from "@/components/seo/MetaTags";
import { StreamFieldRenderer } from "@/components/StreamFieldRenderer";
import { SiteMenu } from "@/components/layout/SiteMenu";
import { SiteInteractions } from "@/components/layout/SiteInteractions";
import { PageNavbar } from "@/components/layout/PageNavbar";
import { PromoBoxModal } from "@/components/layout/PromoBoxModal";
import { PromoBoxProvider } from "@/components/layout/PromoBoxContext";
import { TowerSelectMobile } from "@/components/layout/TowerSelect";
import { pageAppClass, pageBodyClass } from "@/lib/page-classes";
import { PageBodyClasses } from "@/components/layout/PageBodyClasses";
import type { TowerChildPage } from "@/types/page";

interface PageRendererProps {
  page: WagtailPage;
  nav: NavItem[];
  settings: SettingsResponse;
  locale: string;
}

function isHomePage(page: WagtailPage): boolean {
  return page.content_type === "languagerootpage";
}

function isTowersIndexPage(page: WagtailPage): boolean {
  return page.content_type === "towersindexpage";
}

function sectionClass(page: WagtailPage): string {
  const parts = ["themed", "pages"];
  if (page.theme?.id) parts.push(`themed-${page.theme.id}`);
  if (page.theme?.css_class) parts.push(page.theme.css_class);
  if (page.content_type) parts.push(page.content_type);
  if (isHomePage(page)) parts.push("homepage");
  const hasContent = (page.stream_field || []).length > 0 || isTowersIndexPage(page);
  if (!hasContent) parts.push("hero-only");
  return parts.join(" ");
}

/** Full page layout for a WagtailPage payload. */
export function PageRenderer({
  page,
  nav,
  settings,
  locale,
}: PageRendererProps) {
  const appClassName = pageAppClass(page);
  const bodyClassName = pageBodyClass(page);
  const pagePromo = page.promo_box ?? null;

  return (
  <PromoBoxProvider autoShow={Boolean(pagePromo) && isHomePage(page)}>
    <SiteInteractions />
    <PageBodyClasses className={bodyClassName} />

    <MetaTags
      meta={page.meta}
      url={page.url}
      ogImage={page.meta?.og_image}
      fbAppId={page.meta?.fb_app_id}
    />

    <div id="app" className={appClassName}>
      <Header
        nav={nav}
        settings={settings}
        locale={locale}
        pageId={page.id}
        rootPage={settings.root_page}
        languageRoots={settings.language_roots}
      />

      <section className={sectionClass(page)}>
        <Hero
          hero={page.hero}
          locale={locale}
          towerChildren={
            isTowersIndexPage(page)
              ? (page.children as TowerChildPage[])
              : undefined
          }
        />
        <PageNavbar page={page} nav={nav} locale={locale} />
        {isTowersIndexPage(page) ? (
          <TowerSelectMobile
            towers={page.children as TowerChildPage[]}
            locale={locale}
          />
        ) : null}
        <StreamFieldRenderer blocks={page.stream_field || []} locale={locale} />
      </section>

      <div className="transparent" />

      <SiteMenu
        nav={nav}
        page={page}
        locale={locale}
        rootPage={settings.root_page}
        languageRoots={settings.language_roots}
      />

      {pagePromo ? (
        <PromoBoxModal promo={pagePromo} pageId={page.id} locale={locale} />
      ) : null}
    </div>
  </PromoBoxProvider>
  );
}
