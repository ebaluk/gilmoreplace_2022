/**
 * Headless API page payload types shared by blocks and page shells.
 */

export interface WagtailPage {
  id: number;
  title: string;
  slug: string;
  url: string;
  seo_title: string;
  search_description: string;
  show_in_menus: boolean;
  theme: CssTheme | null;
  color_theme: string;
  show_navbar: boolean;
  show_in_sitemap: boolean;
  redirect_to_first_child?: boolean;
  content_page_id?: number;
  hero: HeroData;
  stream_field: StreamFieldBlock[];
  meta: PageMeta;
  content_type?: string;
  language_code: string;
  parent: PageRef | null;
  children: PageRef[];
  promo_box?: PromoBoxData | null;
}

/** Single CTA inside a promo box StreamField. */
export interface PromoBoxLink {
  type: string;
  value: {
    title?: string;
    link_type?: string;
    link?: string | number;
    new_window?: boolean;
    hash?: string;
    resolved_link?: {
      id?: number;
      url?: string;
      title?: string;
      submit_url?: string;
    } | null;
  };
}

/** Promo overlay payload attached to a page or language root. */
export interface PromoBoxData {
  id: number;
  title: string;
  body: string;
  mode: "default" | "image" | "text";
  show_logo: boolean;
  smaller_popup: boolean;
  visible: boolean;
  image: ImageData | null;
  image_ratio: number | null;
  links: PromoBoxLink[];
}

/** Lightweight page reference (parent/children/nav). */
export interface PageRef {
  id: number;
  title: string;
  slug: string;
  url: string;
  show_in_menus?: boolean;
}

/** Tower child page with optional nav icons. */
export interface TowerChildPage extends PageRef {
  icon_desktop?: ImageData | null;
  icon_mobile?: ImageData | null;
}

/** Hero band: title, media, links, optional logos banner. */
export interface HeroData {
  title: string | null;
  text: string | null;
  text_align: string;
  mobile_half_height: boolean;
  video: HeroVideo | null;
  images: ImageData[];
  links: StreamFieldBlock[];
  logos_banner: LogoData[];
  tower_detail?: { number: string } | null;
  text_html?: string | null;
}

/** Hero background video with poster and transcodes. */
export interface HeroVideo {
  id: number;
  title: string;
  poster_url: string | null;
  transcodes: { url: string; mime: string }[];
}

/** Resolved Wagtail image rendition. */
export interface ImageData {
  id: number;
  title: string;
  width: number;
  height: number;
  url: string;
  alt: string;
}

/** Logos banner entry (resolved image + optional link). */
export interface LogoData {
  logo: number | null;
  resolved_logo: ImageData | null;
  link: string | null;
}

/** CMS CSS theme snippet (may include rendered_css). */
export interface CssTheme {
  id: number;
  title: string;
  css_class: string | null;
  color: string;
  background: string;
  rendered_css?: string;
}

/** SEO / Open Graph fields for the page. */
export interface PageMeta {
  site_name: string;
  title: string;
  description: string;
  og_image: ImageData | null;
  fb_app_id: string | null;
  keywords: string;
}

/** One StreamField block; `value` shape depends on `type`. */
export interface StreamFieldBlock {
  type: string;
  id: string;
  value: Record<string, unknown>;
}
