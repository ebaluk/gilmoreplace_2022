"""Settings endpoint schemas."""

from __future__ import annotations

from .common import ApiModel, ImageData


class SiteSettings(ApiModel):
    caption: str = ""
    logo: ImageData | None = None
    ga_view_id: int = 0


class PageMeta(ApiModel):
    site_name: str = "Gilmore Place"
    default_title: str | None = None
    default_description: str | None = None
    default_keywords: str | None = None
    default_image: ImageData | None = None
    fb_app_id: str | None = None


class HeaderPromoBox(ApiModel):
    title: str
    page_id: int


class FooterSocialLink(ApiModel):
    title: str
    fontawesome_icon: str = ""
    link: str = ""
    new_window: bool = False


class RootPageSettings(ApiModel):
    id: int
    phone: str = ""
    email: str = ""
    footer_legal: str = ""
    contact_page_url: str | None = None
    penthouse_collections_url: str | None = None
    header_promo_box: HeaderPromoBox | None = None
    footer_social_links: list[FooterSocialLink] = []
    page_404_title: str | None = None
    page_404_text: str | None = None
    page_404_image: ImageData | None = None


class LanguageRoot(ApiModel):
    language_code: str
    url: str
    label: str = ""


class SettingsResponse(ApiModel):
    """GET /api/v2/headless/settings/"""

    site_settings: SiteSettings
    page_meta: PageMeta
    root_page: RootPageSettings | None = None
    language_roots: list[LanguageRoot] = []
