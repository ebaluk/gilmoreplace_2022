"""Headless HTTP views consumed by the Next.js frontend.

Endpoints are mounted under ``/api/v2/headless/`` (see ``api_router.headless_urls``).
Most GETs accept ``locale`` (default ``en-us``) to select a ``LanguageRootPage``.
"""

from django.conf import settings
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from wagtail.models import Page, Site
from wagtail.images import get_image_model

from .serializers import (
    resolve_image,
    resolve_streamfield_blocks,
    resolve_form,
    serialize_form_field,
    get_promo_box_for_page,
    serialize_promo_box_item,
    _serialize_interactive_map,
    _serialize_google_maps,
)

from .schemas import (
    SettingsResponse,
    FormSubmitResult,
    FormDetailResponse,
    PageResponse,
    dump_model,
)
from .page_urls import page_public_path

Image = get_image_model()


class PageDetailView(APIView):
    """
    Single page with resolved StreamField, hero, SEO meta, and promo box.

    GET /api/v2/headless/pages/<id>/
    GET /api/v2/headless/pages/by-slug/?slug=<slug>&locale=<locale>

    Query params (slug route):
        slug: Relative path under the language root (e.g. ``homes/features``).
        locale: Wagtail language code (default ``en-us``).

    Returns:
        Full page JSON (id, title, stream_field, hero, meta, children, …).
    """

    permission_classes = [AllowAny]

    def get(self, request, page_id=None):
        """Resolve page by id or by slug+locale, then serialize."""
        if page_id:
            try:
                page = Page.objects.get(id=page_id)
            except Page.DoesNotExist:
                raise Http404
        else:
            slug = request.query_params.get("slug")
            locale = request.query_params.get("locale", "en-us")
            from wthomepage.models import LanguageRootPage
            try:
                root = LanguageRootPage.objects.get(language_code=locale)
            except LanguageRootPage.DoesNotExist:
                raise Http404
            if not slug:
                page = root
            else:
                try:
                    if '/' in slug:
                        url_path = root.url_path.rstrip('/') + '/' + slug + '/'
                        page = Page.objects.get(url_path=url_path)
                    else:
                        page = Page.objects.get(slug=slug, path__startswith=root.path)
                except Page.DoesNotExist:
                    raise Http404

        return self._serialize_page(page, request)

    def _serialize_page(self, page, request, *, follow_first_child=True):
        """Build the headless page payload for ``page`` (handles redirect-to-first-child)."""
        specific = page.specific
        content_source = specific
        content_page_id = page.id
        redirect_to_first_child = getattr(specific, "redirect_to_first_child", False)

        if follow_first_child and redirect_to_first_child:
            first_child = page.get_children().live().first()
            if first_child:
                content_source = first_child.specific
                content_page_id = first_child.id

        # Build hero data
        try:
            hero_data = self._get_hero_data(content_source, page=page)
        except Exception:
            hero_data = {"title": page.title, "text": "", "video": None, "images": [], "links": []}

        stream_data = self._get_stream_data(content_source, page=page)

        # Build meta / SEO data
        try:
            meta = self._get_meta(specific, page, request)
        except Exception:
            meta = {"site_name": "Gilmore Place", "title": page.title, "description": "", "og_image": None, "fb_app_id": None, "keywords": ""}

        data = {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "content_type": page.content_type.model if page.content_type else "page",
            "url": page_public_path(page, request),
            "seo_title": page.seo_title or "",
            "search_description": page.search_description or "",
            "show_in_menus": page.show_in_menus,
            "theme": self._get_theme(content_source),
            "color_theme": getattr(content_source, "color_theme", "default"),
            "show_navbar": getattr(specific, "show_navbar", False),
            "show_in_sitemap": getattr(specific, "show_in_sitemap", True),
            "redirect_to_first_child": redirect_to_first_child if follow_first_child else False,
            "content_page_id": content_page_id,
            "hero": hero_data,
            "stream_field": stream_data,
            "meta": meta,
            "language_code": self._get_language_code(specific),
            "parent": self._serialize_parent(page),
            "children": self._serialize_children(page),
            "promo_box": get_promo_box_for_page(page),
        }

        return Response(dump_model(PageResponse, data))

    def _get_stream_data(self, specific, page=None):
        try:
            if not hasattr(specific, "stream_field"):
                return []
            stream_field = specific.stream_field
            if stream_field is None:
                return []
            raw = getattr(stream_field, "raw_data", None)
            if raw:
                return resolve_streamfield_blocks(raw, page=page)
            blocks = list(stream_field)
            if not blocks:
                return []
            return [{"type": b.block_type, "id": b.id, "value": b.value} for b in blocks]
        except Exception:
            return []

    def _get_hero_data(self, specific, page=None):
        data = {
            "title": getattr(specific, "hero_title", None),
            "text": getattr(specific, "hero_text", None),
            "text_align": getattr(specific, "hero_text_align", "left"),
            "mobile_half_height": getattr(specific, "hero_mobile_half_height", True),
            "video": self._resolve_hero_video(specific),
            "images": self._resolve_hero_images(specific),
            "links": self._resolve_hero_links(specific),
            "logos_banner": self._resolve_logos_banner(specific),
        }
        tower_detail = self._get_tower_detail(page or specific)
        if tower_detail:
            data["tower_detail"] = tower_detail
        return data

    def _get_tower_detail(self, page):
        from .serializers import _get_tower_page

        tower_page = _get_tower_page(page)
        if not tower_page or not tower_page.tower_type_id:
            return None
        return {"number": tower_page.tower_type.title}

    def _resolve_hero_video(self, specific):
        video = getattr(specific, "hero_video", None)
        if not video:
            return None
        from .serializers import resolve_video
        try:
            return resolve_video(video.id)
        except Exception:
            return {"id": video.id, "title": str(video)}

    def _resolve_hero_images(self, specific):
        hero_images_attr = getattr(specific, "hero_images", None)
        if hero_images_attr is None:
            return []
        return [
            resolve_image(img.image_id) for img in hero_images_attr.all() if img.image_id
        ]

    def _resolve_hero_links(self, specific):
        links = getattr(specific, "hero_links", None)
        if not links:
            return []
        raw = getattr(links, "raw_data", None)
        if raw is None:
            # If no raw_data, iterate the blocks
            result = []
            for block in links:
                result.append({
                    "type": block.block_type,
                    "id": block.id,
                    "value": block.value,
                })
            return result
        return resolve_streamfield_blocks(raw)

    def _resolve_logos_banner(self, specific):
        logos = getattr(specific, "logos_banner", None)
        if not logos:
            return []
        resolved = []
        for block in logos:
            value = block.value
            resolved.append({
                "logo": value.get("logo"),
                "resolved_logo": resolve_image(value.get("logo")),
                "link": value.get("link"),
            })
        return resolved

    def _get_theme(self, specific):
        theme = getattr(specific, "theme", None)
        if not theme:
            return None
        return {
            "id": theme.id,
            "title": theme.title,
            "css_class": theme.css_class,
            "color": theme.color,
            "background": theme.background,
        }

    def _get_meta(self, specific, page, request):
        from wagtail.contrib.settings.models import BaseSiteSetting
        from wtpagemeta.models import WtPageMeta

        try:
            pm = WtPageMeta.for_request(request)
        except:
            pm = BaseSiteSetting.objects.filter(instance=WtPageMeta).first()

        meta = {
            "site_name": pm.site_name if pm else "Gilmore Place",
            "title": page.seo_title or getattr(specific, "seo_keywords", None) or page.title,
            "description": page.search_description or "",
            "og_image": None,
            "fb_app_id": pm.fb_app_id if pm else None,
            "keywords": getattr(specific, "seo_keywords", ""),
        }

        og_image = getattr(specific, "open_graph_image", None)
        if og_image:
            meta["og_image"] = resolve_image(og_image.id)
        elif pm and pm.default_image_id:
            meta["og_image"] = resolve_image(pm.default_image_id)

        return meta

    def _get_language_code(self, specific):
        return getattr(specific, "language_code", settings.LANGUAGE_CODE)

    def _serialize_parent(self, page):
        parent = page.get_parent()
        if not parent:
            return None
        if not parent.specific_class or parent.specific_class.__name__ == "RootPage":
            return None
        return {
            "id": parent.id,
            "title": parent.title,
            "slug": parent.slug,
            "url": page_public_path(parent),
        }

    def _serialize_children(self, page):
        specific = page.specific
        is_tower_index = getattr(specific, "is_tower_index_page", False)
        if is_tower_index:
            children = page.get_children().live().specific()
        else:
            children = page.get_children().live().in_menu()

        result = []
        for child in children:
            item = {
                "id": child.id,
                "title": child.title,
                "slug": child.slug,
                "url": page_public_path(child),
                "show_in_menus": child.show_in_menus,
            }
            if is_tower_index and child.content_type.model == "towerpage":
                icon_desktop_id = getattr(child, "icon_desktop_id", None)
                icon_mobile_id = getattr(child, "icon_mobile_id", None)
                if icon_desktop_id:
                    item["icon_desktop"] = resolve_image(
                        icon_desktop_id, "fill-157x145-c100"
                    )
                if icon_mobile_id:
                    item["icon_mobile"] = resolve_image(
                        icon_mobile_id, "fill-145x145-c100"
                    )
            result.append(item)
        return result


class PagePreviewView(PageDetailView):
    """
    Draft page payload for Wagtail admin preview (wagtail-headless-preview token).

    GET /api/v2/headless/pages/preview/?content_type=<app.model>&token=<token>

    Requires header ``X-Preview-Secret`` (or ``?secret=``) matching ``PREVIEW_SECRET``.
    """

    def get(self, request, page_id=None):
        from django.apps import apps
        from django.conf import settings
        from django.core.signing import BadSignature

        from wtpages.headless import NextHeadlessPreviewMixin

        expected = getattr(settings, "PREVIEW_SECRET", "") or ""
        provided = (
            request.headers.get("X-Preview-Secret")
            or request.query_params.get("secret")
            or ""
        )
        if not expected or provided != expected:
            raise Http404

        content_type = request.query_params.get("content_type")
        token = request.query_params.get("token")
        if not content_type or not token or "." not in content_type:
            raise Http404

        app_label, model_name = content_type.split(".", 1)
        try:
            model_class = apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404

        if not issubclass(model_class, NextHeadlessPreviewMixin):
            raise Http404

        try:
            page = model_class.get_page_from_preview_token(token)
        except BadSignature:
            raise Http404

        if page is None:
            raise Http404

        # Do not swap in live first-child content while editing a parent draft.
        return self._serialize_page(page, request, follow_first_child=False)


class AllPagesView(APIView):
    """
    List live descendant pages under a language root (for SSG / sitemaps).

    GET /api/v2/headless/pages/?locale=en-us

    Query params:
        locale: Wagtail language code (default ``en-us``).

    Returns:
        ``{"pages": [...]}`` with id, title, slug, url, SEO fields, content_type.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        locale = request.query_params.get("locale", "en-us")
        from wthomepage.models import LanguageRootPage
        try:
            root = LanguageRootPage.objects.get(language_code=locale)
        except LanguageRootPage.DoesNotExist:
            return Response({"pages": []})

        pages = Page.objects.live().descendant_of(root).specific()
        result = []
        for page in pages:
            result.append({
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "url": page_public_path(page, request),
                "seo_title": page.seo_title or "",
                "search_description": page.search_description or "",
                "show_in_menus": page.show_in_menus,
                "content_type": page.content_type.model if page.content_type else "page",
                "language_code": getattr(page, "language_code", locale),
            })
        return Response({"pages": result})


class NavigationView(APIView):
    """
    Nested menu tree for a language root (in-menu / show_navbar rules).

    GET /api/v2/headless/navigation/?locale=en-us

    Query params:
        locale: Wagtail language code (default ``en-us``).

    Returns:
        ``{"items": [NavItem, ...]}`` where each item may include ``children``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        locale = request.query_params.get("locale", "en-us")
        from wthomepage.models import LanguageRootPage
        try:
            root = LanguageRootPage.objects.get(language_code=locale)
        except LanguageRootPage.DoesNotExist:
            return Response({"items": []})

        # Get top-level menu items (direct children of root that are in menus)
        items = root.get_children().live().in_menu().specific()
        nav = []
        for item in items:
            nav.append(self._build_nav_item(item))
        return Response({"items": nav})

    def _build_nav_item(self, page):
        """Serialize one menu node and up to two levels of children."""
        specific = page.specific
        show_navbar = getattr(specific, "show_navbar", False)
        children_qs = page.get_children().live()
        if not show_navbar:
            children_qs = children_qs.in_menu()

        nav_children = []
        for child in children_qs:
            child_specific = child.specific
            child_item = {
                "id": child.id,
                "title": child.title,
                "slug": child.slug,
                "url": page_public_path(child),
                "show_navbar": getattr(child_specific, "show_navbar", False),
                "children": [],
            }
            if getattr(child_specific, "show_navbar", False):
                for sub in child.get_children().live():
                    sub_specific = sub.specific
                    child_item["children"].append({
                        "id": sub.id,
                        "title": sub.title,
                        "slug": sub.slug,
                        "url": page_public_path(sub),
                        "show_navbar": getattr(sub_specific, "show_navbar", False),
                        "children": [],
                    })
            nav_children.append(child_item)

        return {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "content_type": page.content_type.model if page.content_type else "page",
            "url": page_public_path(page),
            "show_navbar": show_navbar,
            "children": nav_children,
        }


class SettingsView(APIView):
    """
    Site chrome settings: logo, SEO defaults, language root contacts, 404 copy.

    GET /api/v2/headless/settings/?locale=en-us

    Query params:
        locale: Selects which ``LanguageRootPage`` to use for ``root_page``.

    Returns:
        ``site_settings``, ``page_meta``, ``root_page``, ``language_roots``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from wtadmin.models import WtSettings
        from wtpagemeta.models import WtPageMeta
        from wthomepage.models import LanguageRootPage

        locale = request.query_params.get("locale", "en-us")

        # WtSettings
        wt_settings = WtSettings.for_request(request) if hasattr(WtSettings, 'for_request') else None
        settings_data = {
            "caption": wt_settings.caption if wt_settings else "",
            "logo": resolve_image(wt_settings.logo_id) if wt_settings and wt_settings.logo_id else None,
            "ga_view_id": wt_settings.ga_view_id if wt_settings else 0,
        }

        # WtPageMeta
        page_meta = WtPageMeta.for_request(request) if hasattr(WtPageMeta, 'for_request') else None
        meta_data = {
            "site_name": page_meta.site_name if page_meta else "Gilmore Place",
            "default_title": page_meta.default_title if page_meta else "",
            "default_description": page_meta.default_description if page_meta else "",
            "default_keywords": page_meta.default_keywords if page_meta else "",
            "default_image": resolve_image(page_meta.default_image_id) if page_meta and page_meta.default_image_id else None,
            "fb_app_id": page_meta.fb_app_id if page_meta else None,
        }

        root_page = None
        try:
            root_page = LanguageRootPage.objects.get(language_code=locale)
        except LanguageRootPage.DoesNotExist:
            root_page = LanguageRootPage.objects.first()

        root_data = None
        if root_page:
            contact_url = None
            if root_page.contact_page_link_id:
                contact_url = page_public_path(root_page.contact_page_link, request)
            penthouse_url = None
            if root_page.penthouse_collections_page_id:
                penthouse_url = page_public_path(
                    root_page.penthouse_collections_page, request
                )

            header_promo_box = None
            if root_page.promo_box_id and root_page.promo_box.visible:
                header_promo_box = {
                    "title": root_page.promo_box.title,
                    "page_id": root_page.id,
                }

            root_data = {
                "id": root_page.id,
                "phone": root_page.phone,
                "email": root_page.email,
                "footer_legal": str(root_page.footer_legal) if root_page.footer_legal else "",
                "contact_page_url": contact_url,
                "penthouse_collections_url": penthouse_url,
                "header_promo_box": header_promo_box,
                "footer_social_links": [
                    {
                        "title": link.title,
                        "fontawesome_icon": link.fontawesome_icon,
                        "link": link.link,
                        "new_window": link.new_window,
                    }
                    for link in root_page.footer_social_links.all()
                ],
                "page_404_title": root_page.page_404_title,
                "page_404_text": str(root_page.page_404_text) if root_page.page_404_text else "",
                "page_404_image": resolve_image(root_page.page_404_image_id),
            }

        language_roots = []
        for lrp in LanguageRootPage.objects.live():
            language_roots.append({
                "language_code": lrp.language_code,
                "url": page_public_path(lrp, request),
                "label": lrp.lang_translated,
            })

        payload = {
            "site_settings": settings_data,
            "page_meta": meta_data,
            "root_page": root_data,
            "language_roots": language_roots,
        }
        return Response(dump_model(SettingsResponse, payload))


class ThemeView(APIView):
    """
    List CMS CSS themes (class names, colors, rendered CSS, background images).

    GET /api/v2/headless/themes/

    Returns:
        ``{"themes": [...]}`` including ``rendered_css`` for injection.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from wtpages.csstheme import CssTheme
        themes = CssTheme.objects.all()
        data = []
        for theme in themes:
            data.append({
                "id": theme.id,
                "title": theme.title,
                "css_class": theme.css_class,
                "color": theme.color,
                "background": theme.background,
                "title_color": theme.title_color,
                "title_background": theme.title_background,
                "css": theme.css,
                "rendered_css": theme.render_theme(),
                "images": [
                    {
                        "id": img.id,
                        "image": resolve_image(img.image_id),
                        "position": img.position,
                        "background_size": img.background_size,
                        "background_position": img.background_position,
                        "scroll_animate": img.scroll_animate,
                        "inside_container": img.inside_container,
                    }
                    for img in theme.images.all()
                ],
            })
        return Response({"themes": data})


class TowerDataView(APIView):
    """
    Bedroom/penthouse type labels and shared StreamField blocks for towers.

    GET /api/v2/headless/towers/

    Returns:
        ``bedroom_types``, ``penthouse_types`` (with zh titles), ``shared_blocks``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from towers.models import (
            TowerBedroomTypes,
            TowerPenthouseTypes,
            SharedPageBlocks,
        )

        bedroom_types = TowerBedroomTypes.objects.filter(visible=True)
        penthouse_types = TowerPenthouseTypes.objects.filter(visible=True)
        shared_blocks = SharedPageBlocks.objects.all()

        return Response({
            "bedroom_types": [
                {
                    "id": bt.id,
                    "title": bt.title,
                    "title_zh_hans": bt.title_zh_hans,
                    "title_zh_hant": bt.title_zh_hant,
                    "sort_order": bt.sort_order,
                }
                for bt in bedroom_types
            ],
            "penthouse_types": [
                {
                    "id": pt.id,
                    "title": pt.title,
                    "title_zh_hans": pt.title_zh_hans,
                    "title_zh_hant": pt.title_zh_hant,
                    "sort_order": pt.sort_order,
                }
                for pt in penthouse_types
            ],
            "shared_blocks": [
                {
                    "id": sb.id,
                    "title": sb.title,
                    "stream_field": resolve_streamfield_blocks(sb.stream_field.raw_data),
                }
                for sb in shared_blocks
            ],
        })


class InteractiveMapsView(APIView):
    """
    All interactive site maps (layout image + points).

    GET /api/v2/headless/maps/

    Returns:
        ``{"maps": [...]}`` via ``_serialize_interactive_map``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from interactivemaps.models import InteractiveMaps
        maps = InteractiveMaps.objects.all()
        return Response({
            "maps": [_serialize_interactive_map(m) for m in maps]
        })


class GoogleMapsInstancesView(APIView):
    """
    Interactive Google Maps snippet instances (places, styles, markers).

    GET /api/v2/headless/google-maps/

    Returns:
        ``{"instances": [...]}`` via ``_serialize_google_maps``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from interactivegooglemaps.models import InteractiveGoogleMaps
        instances = InteractiveGoogleMaps.objects.all()
        return Response({
            "instances": [_serialize_google_maps(m) for m in instances]
        })


class FormDetailView(APIView):
    """
    WtForm definition: fields, submit URL, reCAPTCHA flags.

    GET /api/v2/headless/forms/<id>/

    Returns:
        id, title, submit_url, fields[], enable_recaptcha, recaptcha_site_key.
    """

    permission_classes = [AllowAny]

    def get(self, request, form_id):
        form_data = resolve_form(form_id)
        if not form_data:
            raise Http404

        from wtforms.models import WtForm
        try:
            form = WtForm.objects.get(id=form_id)
        except WtForm.DoesNotExist:
            raise Http404

        fields = form.get_form_fields()
        form_data["fields"] = [
            serialize_form_field(f, num) for num, f in enumerate(fields, start=1)
        ]
        form_data["enable_recaptcha"] = form.enable_recaptcha
        form_data["recaptcha_site_key"] = form.recaptcha_sitekey or settings.RECAPTCHA_SITEKEY

        return Response(dump_model(FormDetailResponse, form_data))


class FormSubmitView(APIView):
    """
    Accept multipart form POST, validate, store submission, optional thank-you URL.

    POST /api/v2/headless/forms/<id>/submit/

    Body:
        multipart/form-data matching WtForm fields (plus reCAPTCHA when enabled).

    Returns:
        On success ``status=success`` with message fields and optional ``thank_you_url``.
        On validation error HTTP 400 with ``status=error`` and ``errors`` map.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, form_id):
        """Validate and process a WtForm submission."""
        from wtforms.models import WtForm
        try:
            obj = WtForm.objects.get(id=form_id)
        except WtForm.DoesNotExist:
            raise Http404

        form = obj.get_form(request.POST, request.FILES)

        if form.is_valid():
            obj.handle_files_upload(form, request)
            obj.process_form_submission(form, request)
            thank_you_url = (
                page_public_path(obj.selected_thank_you_page)
                if obj.selected_thank_you_page
                else None
            )
            payload = {
                "status": "success",
                "message_text": obj.thank_you_text,
                "message_title": obj.title,
                "call_js_on_success": obj.call_js_on_success,
                "thank_you_url": thank_you_url,
            }
            return Response(dump_model(FormSubmitResult, payload))
        else:
            errors = {}
            for field_name, field_errors in form.errors.items():
                errors[field_name] = [str(e) for e in field_errors]
            payload = {
                "status": "error",
                "errors": errors,
            }
            return Response(
                dump_model(FormSubmitResult, payload),
                status=status.HTTP_400_BAD_REQUEST,
            )


class InstagramFeedView(APIView):
    """
    Cached Instagram feed items from stored tokens.

    GET /api/v2/headless/instagram/

    Returns:
        ``{"feed": [{id, image_url, link, caption, created_time}, ...]}``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        from wtinstagramtokens.models import WtInstagramToken
        tokens = WtInstagramToken.objects.all()
        feed = []
        for token in tokens:
            items = token.social_content_items.all().order_by("-created_time")[:20]
            for item in items:
                feed.append({
                    "id": item.id,
                    "image_url": item.image_url,
                    "link": item.link,
                    "caption": item.caption,
                    "created_time": item.created_time.isoformat() if item.created_time else None,
                })
        return Response({"feed": feed})


class PromoBoxView(APIView):
    """
    Promo box overlay payload for a page (or null if none).

    GET /api/v2/headless/promobox/?page_id=<id>

    Query params:
        page_id: Wagtail page primary key.

    Returns:
        ``{"promo_box": {...} | null}``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response({"promo_box": None})

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"promo_box": None})

        return Response({"promo_box": get_promo_box_for_page(page)})


class RebuildWebhookView(APIView):
    """
    Ack webhook for CMS publish → Next.js ISR revalidation (secret-gated).

    POST /api/v2/headless/revalidate/

    Body JSON:
        secret: Must match ``settings.REVALIDATION_SECRET``.
        page_id: Optional Wagtail page id for targeted revalidate.

    Returns:
        ``{"revalidated": true, "page_id": ...}`` or HTTP 403 on bad secret.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate secret and acknowledge revalidation request."""
        secret = request.data.get("secret")
        expected = getattr(settings, "REVALIDATION_SECRET", None)
        if not expected or secret != expected:
            return Response({"error": "Invalid secret"}, status=status.HTTP_403_FORBIDDEN)
        page_id = request.data.get("page_id")
        # The actual revalidation is done by the Next.js side
        # This endpoint acknowledges the request
        return Response({"revalidated": True, "page_id": page_id})


class ImageRenditionView(APIView):
    """
    Wagtail image rendition URL for a filter spec.

    GET /api/v2/headless/images/<id>/<filter_spec>/

    Example:
        ``/api/v2/headless/images/123/width-800/``

    Returns:
        id, title, url, width, height, alt, filter_spec.
    """

    permission_classes = [AllowAny]

    def get(self, request, image_id, filter_spec):
        from wagtail.images import get_image_model
        Image = get_image_model()
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            raise Http404

        try:
            rendition = image.get_rendition(filter_spec)
        except Exception:
            raise Http404

        return Response({
            "id": image.id,
            "title": image.title,
            "url": rendition.url,
            "width": rendition.width,
            "height": rendition.height,
            "alt": image.title,
            "filter_spec": filter_spec,
        })
