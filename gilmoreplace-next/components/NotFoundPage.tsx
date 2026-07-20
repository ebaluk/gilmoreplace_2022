"use client";


/**
 * 404 experience using language-root settings (copy/image) and site chrome.
 */
import { useQuery } from "@tanstack/react-query";
import { Header } from "@/components/layout/Header";
import { Hero } from "@/components/layout/Hero";
import { SiteInteractions } from "@/components/layout/SiteInteractions";
import { PageBodyClasses } from "@/components/layout/PageBodyClasses";
import { SiteMenu } from "@/components/layout/SiteMenu";
import { MetaTags } from "@/components/seo/MetaTags";
import {
  type NavItem,
  type RootPageSettings,
  type SettingsResponse,
} from "@/lib/api/client";
import { navigationQuery, settingsQuery } from "@/lib/api/queries";
import type { HeroData, WagtailPage } from "@/types/page";

const FALLBACK_SETTINGS: SettingsResponse = {
  site_settings: { caption: "", logo: null, ga_view_id: 0 },
  page_meta: {
    site_name: "Gilmore Place",
    default_title: null,
    default_description: "",
    default_keywords: "",
    default_image: null,
    fb_app_id: null,
  },
  root_page: null,
  language_roots: [],
};

function notFoundStubPage(locale: string): WagtailPage {
  return {
    id: 0,
    title: "404",
    slug: "404",
    url: `/${locale}/404`,
    seo_title: "",
    search_description: "",
    show_in_menus: false,
    theme: null,
    color_theme: "default",
    show_navbar: false,
    show_in_sitemap: false,
    hero: {
      title: null,
      text: null,
      text_align: "left",
      mobile_half_height: true,
      video: null,
      images: [],
      links: [],
      logos_banner: [],
    },
    stream_field: [],
    meta: {
      site_name: "Gilmore Place",
      title: "Page Not Found",
      description: "",
      og_image: null,
      fb_app_id: null,
      keywords: "",
    },
    language_code: locale,
    parent: null,
    children: [],
  };
}

function buildNotFoundHero(rootPage: RootPageSettings | null | undefined): HeroData {
  if (rootPage?.page_404_title || rootPage?.page_404_text || rootPage?.page_404_image) {
    return {
      title: rootPage.page_404_title || "404",
      text: null,
      text_html: rootPage.page_404_text || null,
      text_align: "left",
      mobile_half_height: true,
      video: null,
      images: rootPage.page_404_image ? [rootPage.page_404_image] : [],
      links: [],
      logos_banner: [],
    };
  }

  return {
    title: "404",
    text: "Page not found",
    text_align: "left",
    mobile_half_height: true,
    video: null,
    images: [],
    links: [],
    logos_banner: [],
  };
}

interface NotFoundPageShellProps {
  locale: string;
  nav: NavItem[];
  settings: SettingsResponse;
}

function NotFoundPageShell({ locale, nav, settings }: NotFoundPageShellProps) {
  const rootPage = settings.root_page;
  const hero = buildNotFoundHero(rootPage);
  const stubPage = notFoundStubPage(locale);

  return (
    <>
      <SiteInteractions />
      <PageBodyClasses className="color-theme-default" />

      <MetaTags
        meta={{
          site_name: settings.page_meta.site_name,
          title: rootPage?.page_404_title || "Page Not Found",
          description: settings.page_meta.default_description || "",
          keywords: settings.page_meta.default_keywords || "",
          og_image: rootPage?.page_404_image ?? settings.page_meta.default_image,
          fb_app_id: settings.page_meta.fb_app_id,
        }}
        url={stubPage.url}
        ogImage={rootPage?.page_404_image ?? settings.page_meta.default_image}
        fbAppId={settings.page_meta.fb_app_id}
      />

      <div id="app" className="page-404 color-theme-default">
        <Header
          nav={nav}
          settings={settings}
          locale={locale}
          rootPage={settings.root_page}
          languageRoots={settings.language_roots}
        />

        <section className="themed pages page-404">
          <Hero hero={hero} locale={locale} />
        </section>

        <div className="transparent" />

        <SiteMenu
          nav={nav}
          page={stubPage}
          locale={locale}
          rootPage={settings.root_page}
          languageRoots={settings.language_roots}
        />
      </div>
    </>
  );
}

/** Client 404 page for a given locale. */
export function NotFoundPage({ locale }: { locale: string }) {
  const navQuery = useQuery(navigationQuery(locale));
  const settingsQueryResult = useQuery(settingsQuery(locale));

  const nav = navQuery.data?.items ?? [];
  const settings = settingsQueryResult.data ?? FALLBACK_SETTINGS;

  return <NotFoundPageShell locale={locale} nav={nav} settings={settings} />;
}
