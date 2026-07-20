"""Resolve Wagtail StreamField / media IDs into JSON for the headless API."""

from django.conf import settings
from django.urls import reverse

from rest_framework import serializers

from wagtail.images import get_image_model
Image = get_image_model()


def resolve_image(image_id, rendition_spec="width-800"):
    """
    Resolve a Wagtail image ID to a JSON-ready dict with rendition URL.

    Returns:
        dict with id, title, width, height, url, alt; or None if missing.
    """
    if not image_id:
        return None
    try:
        image = Image.objects.get(id=image_id)
        rendition = image.get_rendition(rendition_spec)
        return {
            "id": image.id,
            "title": image.title,
            "width": image.width,
            "height": image.height,
            "url": rendition.url,
            "alt": image.title,
        }
    except Image.DoesNotExist:
        return None


def resolve_document(doc_id):
    """
    Resolve a Wagtail document ID to download metadata.

    Returns:
        dict with id, title, url, filename; or None if missing.
    """
    if not doc_id:
        return None
    from wagtail.documents import get_document_model
    Document = get_document_model()
    try:
        doc = Document.objects.get(id=doc_id)
        return {
            "id": doc.id,
            "title": doc.title,
            "url": doc.url,
            "filename": doc.filename,
        }
    except Document.DoesNotExist:
        return None


def resolve_page(page_id):
    """
    Resolve a Wagtail page ID to a short page reference.

    Returns:
        dict with id, title, url, slug; or None if missing.
    """
    if not page_id:
        return None
    from wagtail.models import Page
    try:
        page = Page.objects.get(id=page_id)
        return {
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "slug": page.slug,
        }
    except Page.DoesNotExist:
        return None


def resolve_video(video_id):
    """
    Resolve a wagtailvideos Video ID including ready transcodes and poster.

    Returns:
        dict with id, title, poster, transcodes[]; or None if missing.
    """
    if not video_id:
        return None
    from wagtailvideos.models import Video
    try:
        video = Video.objects.get(id=video_id)
        transcodes = []
        items = video.transcodes.exclude(processing=True).filter(error_message__exact="")
        for item in items:
            transcodes.append({"url": item.url, "mime": "video/%s" % item.media_format})
        poster_url = None
        if hasattr(video, 'thumbnail') and video.thumbnail:
            poster_url = video.thumbnail.url
        return {
            "id": video.id,
            "title": video.title,
            "poster_url": poster_url,
            "transcodes": transcodes,
        }
    except Video.DoesNotExist:
        return None


def resolve_streamfield_blocks(stream_data, page=None):
    """
    Deep-resolve StreamField raw_data into JSON-safe block dicts for the headless API.

    Returns:
        List of ``{"type", "value", ...}`` blocks with nested media/links expanded.
    """
    if not stream_data:
        return []

    resolved = []
    for block in stream_data:
        block_type = block.get("type")
        value = block.get("value", {})
        resolved_block = {
            "type": block_type,
            "id": block.get("id"),
            "value": _resolve_block_value(block_type, value, page=page),
        }
        resolved.append(resolved_block)
    return resolved


def _get_tower_page(page):
    """Walk ancestors to find the nearest TowerPage for context-aware blocks."""
    if not page:
        return None
    from towers.models import TowerPage

    specific = page.specific
    if isinstance(specific, TowerPage):
        return specific
    return TowerPage.objects.ancestor_of(page).live().first()


def _resolve_block_value(block_type, value, page=None):
    """Dispatch a single stream block type to the matching ``_resolve_*`` helper."""
    if block_type == "form":
        return _resolve_form_chooser(value)
    if block_type == "tower_plans":
        return _resolve_tower_plans(value, page=page)
    if block_type == "tower_views":
        return _resolve_tower_views(value, page=page)
    if not isinstance(value, dict):
        return value

    resolvers = {
        "paragraph": _resolve_paragraph,
        "image": _resolve_image_block,
        "gallery": _resolve_gallery,
        "gallery_collections": _resolve_gallery_collections,
        "carousel": _resolve_carousel,
        "video": _resolve_video_block,
        "texts_and_images_gallery": _resolve_texts_images_gallery,
        "about_collage": _resolve_about_collage,
        "form": _resolve_form_chooser,
        "interactive_map": _resolve_interactive_map,
        "interactive_map_tabks": _resolve_interactive_map_tabs,
        "places": _resolve_places,
        "features": _resolve_features,
        "info": _resolve_info,
        "contact": _resolve_contact,
        "penthouses_widget": _resolve_penthouses_widget,
        "site_map": _resolve_simple,
        "raw_html": _resolve_simple,
        "hash": _resolve_simple,
        "onni_logo": _resolve_simple,
        "shared_blocks": _resolve_shared_blocks,
    }

    resolver = resolvers.get(block_type, _resolve_simple)
    if block_type == "shared_blocks":
        return _resolve_shared_blocks(value, page=page)
    return resolver(value)


def _resolve_simple(value):
    """Pass-through resolver for blocks that need no expansion."""
    return value


def _resolve_related_links(links_value):
    """Resolve nested related-links stream (description + link blocks)."""
    if not links_value or not isinstance(links_value, dict):
        return links_value
    resolved = dict(links_value)
    links_list = resolved.get("links")
    if links_list and isinstance(links_list, list):
        for i, link in enumerate(links_list):
            if isinstance(link, dict):
                links_list[i] = _resolve_link_block(link.get("type"), link.get("value", {}))
    return resolved


def _resolve_link_block(link_type, link_value):
    """Attach ``resolved_link`` for page, document, or form chooser links."""
    if link_type == "internal_page_link" and link_value:
        link_value["resolved_link"] = resolve_page(link_value.get("link"))
    elif link_type == "doc_link" and link_value:
        link_value["resolved_link"] = resolve_document(link_value.get("link"))
    elif link_type == "form_link" and link_value:
        link_value["resolved_link"] = resolve_form(link_value.get("link"))
    return {"type": link_type, "value": link_value}


def resolve_form(form_id):
    """
    Build a partial form payload (id, title, submit_url) for a WtForm id.

    Returns:
        dict or None if the form does not exist. Fields are added by FormDetailView.
    """
    if not form_id:
        return None
    from wtforms.models import WtForm
    try:
        form = WtForm.objects.get(id=form_id)
        return {
            "id": form.id,
            "title": form.title,
            "submit_url": reverse("headless_form_submit", kwargs={"form_id": form.id}),
        }
    except WtForm.DoesNotExist:
        return None


def resolve_form_field_choices(field):
    """Parse WtForm field choices into a list of ``{value, label}`` dicts."""
    if field.field_type not in ("dropdown", "dropdown2", "radio", "checkboxes"):
        return []

    if field.lasso_question_list_id:
        return [
            {"value": str(item.lasso_id), "label": item.title}
            for item in field.lasso_question_list.list_items.all()
        ]

    if field.choices:
        return [
            {"value": line.strip(), "label": line.strip()}
            for line in field.choices.splitlines()
            if line.strip()
        ]

    return []


def serialize_form_field(field, num):
    """
    Serialize one WtForm field for the headless form schema.

    Returns:
        dict with id, label, field_type, required, choices, default_value, help_text, clean_name, etc.
    """
    choices_list = resolve_form_field_choices(field)
    return {
        "id": field.id,
        "label": field.label,
        "field_type": field.field_type,
        "required": field.required,
        "choices": field.choices,
        "choices_list": choices_list,
        "default_value": field.default_value,
        "help_text": field.help_text,
        "clean_name": field.clean_name,
        "add_css_class": field.add_css_class or "",
        "num": num,
    }


def _resolve_paragraph(value):
    """Resolve paragraph/text block: theme, image, and related links."""
    resolved = dict(value)
    if value.get("image"):
        if value.get("night_time_image"):
            resolved["resolved_image"] = resolve_image(value["image"], "fill-747x420-c100")
        else:
            resolved["resolved_image"] = resolve_image(value["image"], "max-1024x1024")
    if value.get("night_time_image"):
        resolved["resolved_night_time_image"] = resolve_image(
            value["night_time_image"], "fill-747x420-c100"
        )
    if value.get("new_links"):
        resolved["new_links"] = _resolve_related_links(value["new_links"])
    if value.get("theme"):
        resolved["theme"] = resolve_theme(value["theme"])
    return resolved


def _resolve_image_block(value):
    """Resolve image block with theme and full image rendition."""
    resolved = dict(value)
    if value.get("image"):
        resolved["resolved_image"] = resolve_image(value["image"], "max-1980x1980")
    return resolved


def _serialize_penthouse_plan(plan):
    """Serialize a penthouse floor-plan snippet to JSON."""
    floorplan_url = None
    floorplan_width = None
    floorplan_height = None
    if plan.floorplan_image_id:
        try:
            rendition = plan.floorplan_image.get_rendition("crop_to_content|max-1600x1600")
            floorplan_url = rendition.url
            floorplan_width = rendition.width
            floorplan_height = rendition.height
        except Exception:
            pass

    floorplates_url = None
    if plan.floorplates_image_id:
        try:
            floorplates_url = plan.floorplates_image.get_rendition("max-640x640").url
        except Exception:
            pass

    floorplates_images = []
    try:
        for img in plan.floorplates_image_renditions:
            if img.image:
                floorplates_images.append(img.image.url)
    except Exception:
        pass

    layout = "vertical"
    if floorplan_width and floorplan_height and floorplan_width > floorplan_height:
        layout = "horizontal"

    penthouse_type = None
    if plan.penthouse_type_id:
        pt = plan.penthouse_type
        penthouse_type = {
            "id": pt.id,
            "title": pt.title,
            "title_zh_hans": pt.title_zh_hans,
            "title_zh_hant": pt.title_zh_hant,
            "sort_order": pt.sort_order,
        }

    return {
        "id": plan.id,
        "title": plan.title,
        "sold": plan.sold,
        "interiors": plan.interiors or "",
        "exteriors": plan.exteriors or "",
        "total_sqft": plan.total_sqft or "",
        "penthouse_type": penthouse_type,
        "pdf_url": plan.pdf.url if plan.pdf_id else None,
        "floorplan_image_url": floorplan_url,
        "floorplates_image_url": floorplates_url,
        "floorplates_images": floorplates_images,
        "layout": layout,
    }


def _resolve_tower_plans(value, page=None):
    """Expand tower plans block with bedroom filters and plan images."""
    resolved = dict(value)
    tower_page = _get_tower_page(page)
    if not tower_page or not tower_page.tower_type_id:
        resolved["apartment_types"] = []
        return resolved

    apartment_types = {}
    for plan in tower_page.tower_type.plans.exclude(
        bedrooms__visible=False
    ).select_related("bedrooms"):
        bed = plan.bedrooms
        if bed.id not in apartment_types:
            apartment_types[bed.id] = {
                "id": bed.id,
                "title": bed.title,
                "title_zh_hans": bed.title_zh_hans,
                "title_zh_hant": bed.title_zh_hant,
                "sort_order": bed.sort_order,
                "apartments": [],
            }
        apartment_types[bed.id]["apartments"].append(_serialize_penthouse_plan(plan))

    resolved["apartment_types"] = [
        apartment_types[key]
        for key in sorted(
            apartment_types.keys(),
            key=lambda item: apartment_types[item]["sort_order"],
        )
    ]
    return resolved


def _resolve_tower_views(value, page=None):
    """Expand tower views block with view images/points."""
    resolved = dict(value)
    text = value.get("text")
    if text is not None and not isinstance(text, str):
        resolved["text"] = str(text)

    items = []
    tower_page = _get_tower_page(page)
    if tower_page and tower_page.tower_type_id:
        views_qs = tower_page.tower_type.views.all()
        if value.get("penthouses_only"):
            views_qs = views_qs.filter(penthouse_view=True)
        for view in views_qs.order_by("-sort_order"):
            image_data = None
            if view.image_id:
                image_data = resolve_image(view.image_id, "max-20000x680")
            items.append({
                "id": view.id,
                "title": view.title,
                "image_url": image_data["url"] if image_data else None,
                "image_width": image_data["width"] if image_data else None,
                "image_height": image_data["height"] if image_data else None,
            })
    resolved["items"] = items
    return resolved


def _resolve_penthouses_widget(value):
    """Expand penthouses widget with towers, units, and plan links."""
    from collections import OrderedDict
    from towers.models import Tower

    resolved = dict(value)
    penthouse_types = {}
    towers = []

    for tower in Tower.objects.all().order_by("id"):
        plans = tower.plans.exclude(penthouse_type__isnull=True)
        if not plans.exists():
            continue
        serialized_plans = [_serialize_penthouse_plan(p) for p in plans]
        type_ids = set()
        for p in plans:
            if p.penthouse_type_id and p.penthouse_type_id not in penthouse_types:
                pt = p.penthouse_type
                penthouse_types[p.penthouse_type_id] = {
                    "id": pt.id,
                    "title": pt.title,
                    "title_zh_hans": pt.title_zh_hans,
                    "title_zh_hant": pt.title_zh_hant,
                    "sort_order": pt.sort_order,
                }
            if p.penthouse_type_id:
                type_ids.add(p.penthouse_type_id)

        towers.append({
            "id": tower.id,
            "title": tower.title,
            "penthouse_type_ids": sorted(type_ids),
            "plans": serialized_plans,
        })

    resolved["penthouse_types"] = [
        penthouse_types[k]
        for k in sorted(penthouse_types.keys(), key=lambda x: penthouse_types[x]["sort_order"])
    ]
    resolved["towers"] = towers
    return resolved


def _resolve_gallery(value):
    """Expand gallery block images to rendition URLs."""
    resolved = dict(value)
    if value.get("images"):
        resolved["resolved_images"] = [resolve_image(img_id) for img_id in value["images"] if img_id]
    return resolved


def _resolve_gallery_collections(value):
    """Expand gallery-with-collections into grouped image sets."""
    resolved = dict(value)
    # GalleryCollectionsBlock resolves images server-side in get_context
    # For the API, we compute the same logic here
    from collections import OrderedDict
    from wagtail.models import Collection
    from wagtail.images import get_image_model
    Image = get_image_model()
    from taggit.models import Tag

    collections_data = []
    all_images = OrderedDict()

    for item in value.get("gallery_collections", []):
        title = item.get("title", "")
        collection_id = item.get("collection")
        tag_id = item.get("tag")

        if collection_id:
            try:
                collection = Collection.objects.get(id=collection_id)
                images = Image.objects.filter(collection=collection)
                from django.db.models.expressions import RawSQL
                images = images.annotate(
                    sort_order=RawSQL(
                        "SELECT sort_order FROM wtadmin_wtimagesort WHERE wtadmin_wtimagesort.image_id = wagtailimages_image.id",
                        [],
                    )
                )
                images = images.order_by("sort_order")
                _add_images_to_collection(all_images, images, title)
            except Collection.DoesNotExist:
                pass
        elif tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)
                images = Image.objects.filter(tags=tag)
                from django.db.models.expressions import RawSQL
                images = images.annotate(
                    sort_order=RawSQL(
                        "SELECT sort_order FROM wtadmin_wtimagesortbytag WHERE wtadmin_wtimagesortbytag.image_id = wagtailimages_image.id AND wtadmin_wtimagesortbytag.tag_id = %s",
                        [tag_id],
                    )
                )
                images = images.order_by("sort_order")
                _add_images_to_collection(all_images, images, title)
            except Tag.DoesNotExist:
                pass

    resolved["resolved_images"] = [
        resolve_image(img_id, "max-1920x1920") for img_id in all_images.keys()
    ]
    return resolved


def _add_images_to_collection(image_dict, images, collection_title):
    """Append resolved images into a collection bucket dict."""
    for image in images:
        if image.id not in image_dict:
            image_dict[image.id] = image
            image_dict[image.id].cats = [collection_title]


def _resolve_carousel(value):
    """Expand carousel slides with resolved images and links."""
    resolved = dict(value)
    if value.get("images"):
        rendition_specs = {
            "inside": "fill-1024x638-c100",
            "insidetext": "fill-1024x638-c100",
            "full": "max-1980x1980",
            "condensed": "fill-1980x963-c100",
            "regular": "fill-1905x672-c100",
        }
        spec = rendition_specs.get(value.get("image_size"), "fill-1980x872-c100")
        resolved["resolved_images"] = [
            resolve_image(img_id, spec) for img_id in value["images"] if img_id
        ]
    return resolved


def _resolve_video_block(value):
    """Expand video block with poster and transcoded sources."""
    resolved = dict(value)
    if value.get("video"):
        video_data = resolve_video(value["video"])
        resolved["resolved_video"] = video_data
        if video_data:
            resolved["resolved_transcodes"] = video_data.get("transcodes", [])
    if value.get("poster"):
        resolved["resolved_poster"] = resolve_image(value["poster"])
    return resolved


def _resolve_texts_images_gallery(value):
    """Expand texts-and-images gallery rows/items."""
    resolved = dict(value)
    if value.get("rows"):
        resolved_rows = []
        for row in value["rows"]:
            resolved_row = _resolve_texts_images_row(row)
            resolved_rows.append(resolved_row)
        resolved["resolved_rows"] = resolved_rows
    return resolved


def _resolve_texts_images_row(row):
    """Resolve one texts-and-images gallery row."""
    if not row:
        return row
    resolved = dict(row)
    boxes = row.get("boxes", [])
    if isinstance(boxes, list):
        resolved_boxes = []
        for box in boxes:
            if isinstance(box, dict):
                box_type = box.get("type")
                box_value = box.get("value", {})
                resolved_box = _resolve_texts_images_box(box_type, box_value)
                resolved_boxes.append({"type": box_type, "value": resolved_box})
            else:
                resolved_boxes.append(box)
        resolved["boxes"] = resolved_boxes
    return resolved


def _resolve_texts_images_item(item_type, item_value):
    """Resolve one texts-and-images item (image or text)."""
    if not isinstance(item_value, dict):
        return item_value
    resolved = dict(item_value)
    if item_type == "image" and item_value.get("image"):
        resolved["resolved_image"] = resolve_image(item_value["image"], "max-1300x1300")
    nested = item_value.get("items")
    if nested and isinstance(nested, list):
        resolved["items"] = [
            {
                "type": sub.get("type"),
                "id": sub.get("id"),
                "value": _resolve_texts_images_item(sub.get("type"), sub.get("value", {})),
            }
            if isinstance(sub, dict)
            else sub
            for sub in nested
        ]
    return resolved


def _resolve_texts_images_box(box_type, box_value):
    """Resolve corner/text box nesting inside gallery items."""
    resolved = dict(box_value)
    if box_value.get("image"):
        resolved["resolved_image"] = resolve_image(box_value["image"], "max-1300x1300")
    items = box_value.get("items")
    if items and isinstance(items, list):
        resolved["items"] = [
            {
                "type": item.get("type"),
                "id": item.get("id"),
                "value": _resolve_texts_images_item(item.get("type"), item.get("value", {})),
            }
            if isinstance(item, dict)
            else item
            for item in items
        ]
    return resolved


def _resolve_about_collage(value):
    """Expand About Onni collage image groups and link."""
    resolved = dict(value)
    if value.get("image_groups"):
        resolved_groups = []
        for group in value["image_groups"]:
            resolved_group = dict(group)
            if group.get("images"):
                resolved_group["resolved_images"] = []
                for img in group["images"]:
                    resolved_img = dict(img)
                    if img.get("image"):
                        resolved_img["resolved_image"] = resolve_image(
                            img["image"], "max-640x640"
                        )
                    resolved_group["resolved_images"].append(resolved_img)
            resolved_groups.append(resolved_group)
        resolved["resolved_image_groups"] = resolved_groups
    return resolved


def _resolve_form_chooser(value):
    """Attach resolved form summary to a form-chooser block."""
    resolved = {"form_id": value} if isinstance(value, (int, str)) else dict(value)
    form_id = value if isinstance(value, int) else value.get("form_id")
    if form_id:
        resolved["resolved_form"] = resolve_form(form_id)
    return resolved


def resolve_theme(theme_id):
    """
    Resolve a CssTheme snippet id to id/css_class (and related fields as available).

    Returns:
        theme dict or None.
    """
    if not theme_id:
        return None
    from wtpages.csstheme import CssTheme
    try:
        theme = CssTheme.objects.get(id=theme_id)
        return {"id": theme.id, "css_class": theme.css_class}
    except CssTheme.DoesNotExist:
        return None


def _resolve_interactive_map(value):
    """Attach fully serialized interactive map object to the block."""
    resolved = dict(value)
    map_id = value.get("interactive_map")
    if map_id:
        from interactivemaps.models import InteractiveMaps
        try:
            map_obj = InteractiveMaps.objects.get(id=map_id)
            resolved["resolved_map"] = _serialize_interactive_map(map_obj)
        except InteractiveMaps.DoesNotExist:
            resolved["resolved_map"] = None
    if value.get("theme"):
        resolved["theme"] = resolve_theme(value["theme"])
    return resolved


def _serialize_interactive_map(map_obj):
    """Serialize InteractiveMaps model (layout image + points)."""
    point_list = [
        {
            "id": p.id,
            "title": p.title,
            "body": p.body,
            "left": p.left,
            "top": p.top,
            "visible": p.visible,
            "style": p.style or f"left: {p.left}%; top: {p.top}%;",
            "idx": idx,
        }
        for idx, p in enumerate(
            map_obj.points.filter(visible=True).order_by("sort_order"), start=1
        )
    ]
    return {
        "id": map_obj.id,
        "title": map_obj.title,
        "layout_image": resolve_image(map_obj.layout_image_id),
        "aspect_ratio": map_obj.style,
        "points": point_list,
        "layout_image_points": point_list,
    }


def _resolve_interactive_map_tabs(value):
    """Resolve tabbed interactive maps list."""
    resolved = dict(value)
    maps_list = value.get("maps", [])
    resolved["resolved_maps"] = [_resolve_interactive_map(m) for m in maps_list]
    return resolved


def _resolve_places(value):
    """Resolve places / Google maps instance reference on a block."""
    resolved = dict(value)
    instance_id = value.get("instance")
    if instance_id:
        from interactivegooglemaps.models import InteractiveGoogleMaps
        try:
            instance = InteractiveGoogleMaps.objects.get(id=instance_id)
            resolved["resolved_instance"] = _serialize_google_maps(instance)
        except InteractiveGoogleMaps.DoesNotExist:
            resolved["resolved_instance"] = None
    resolved["google_maps_api_key"] = settings.GOOGLE_MAP_API_KEY
    return resolved


def _serialize_google_maps(instance):
    """Serialize InteractiveGoogleMaps instance (markers, styles)."""
    return {
        "id": instance.id,
        "title": instance.title,
        "latitude": instance.latitude,
        "longitude": instance.longitude,
        "place_groups": [
            {
                "id": g.id,
                "title": g.title,
                "color": g.color,
                "places": [
                    {
                        "type": p.block_type,
                        "value": {
                            "title": p.value.get("title"),
                            "latitude": p.value.get("latitude"),
                            "longitude": p.value.get("longitude"),
                            "address": p.value.get("address"),
                            "url": p.value.get("url"),
                        },
                    }
                    for p in g.places
                ],
            }
            for g in instance.place_groups.all()
        ],
    }


def _resolve_features(value):
    """Resolve features accordion block and download links."""
    resolved = dict(value)
    if value.get("new_links"):
        resolved["new_links"] = _resolve_related_links(value["new_links"])
    return resolved


def _resolve_info(value):
    """Resolve info blocks list with theme."""
    resolved = dict(value)
    return resolved


def _resolve_contact(value):
    """Resolve contact block items with theme."""
    resolved = dict(value)
    return resolved


def _resolve_shared_blocks(value, page=None):
    """Inline shared page blocks stream from a SharedPageBlocks chooser."""
    resolved = dict(value)
    sb_id = value.get("shared_blocks")
    if sb_id:
        from towers.models import SharedPageBlocks
        try:
            sb = SharedPageBlocks.objects.get(id=sb_id)
            resolved["resolved_stream_field"] = resolve_streamfield_blocks(
                sb.stream_field.raw_data, page=page
            )
        except SharedPageBlocks.DoesNotExist:
            pass
    return resolved


def resolve_promo_box_links(raw_data):
    """Resolve promo box StreamField links to usable URLs."""
    if not raw_data:
        return []
    resolved = []
    for block in raw_data:
        block_type = block.get("type")
        value = block.get("value", {})
        if isinstance(value, dict):
            value = dict(value)
        resolved.append(_resolve_link_block(block_type, value))
    return resolved


def serialize_promo_box_item(promo):
    """
    Serialize a promo box snippet for overlays/modals.

    Returns:
        dict with title, copy, images, links, visibility flags.
    """
    image_data = None
    image_ratio = None
    if promo.image_id:
        image_data = resolve_image(promo.image_id, rendition_spec="width-866")
        if promo.image and promo.image.width:
            image_ratio = round((promo.image.height / promo.image.width) * 100, 4)

    raw_links = None
    if promo.links_stream_field:
        raw_links = getattr(promo.links_stream_field, "raw_data", promo.links_stream_field)

    return {
        "id": promo.id,
        "title": promo.title,
        "body": str(promo.body) if promo.body else "",
        "mode": promo.mode,
        "show_logo": promo.show_logo,
        "smaller_popup": promo.smaller_popup,
        "visible": promo.visible,
        "image": image_data,
        "image_ratio": image_ratio,
        "links": resolve_promo_box_links(raw_links),
    }


def get_promo_box_for_page(page):
    """
    Pick the promo box configured for ``page`` (or None if unset/hidden).

    Returns:
        Serialized promo box dict or None.
    """
    from wtpromobox.models import PromoBoxItem

    promo = PromoBoxItem.objects.filter(visible=True, pages__page=page).first()
    if not promo:
        return None
    return serialize_promo_box_item(promo)
