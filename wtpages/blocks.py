from email.policy import default
from random import choices
import uuid
from collections import OrderedDict
from django import forms
from django.forms import widgets
from django.utils.functional import cached_property
from wagtail import blocks
from wagtail.images.models import *
from wagtail.models import Collection
from taggit.models import Tag
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.fields import StreamField
from django.utils.translation import gettext_lazy as _
from wagtail.coreutils import resolve_model_string

from .csstheme import CssTheme
from wtforms.models import WtForm
# from wtinstagramtokens.models import WtInstagramToken
from interactivemaps.models import InteractiveMaps
from interactivegooglemaps.models import InteractiveGoogleMaps
from wagtailvideos.models import Video
# from towers.sharedblocks import SharedPageBlocks

GALLERY_MODE = (
    ('lt-12', 'Thumbnails'),
    ('12', 'Different Shapes'),
)

TEXT_BLOCK_ALIGN_CHOICES = (
    ("left", _("Left")), ("right", _("Right")), ("center", _("Center")),)
PAGE_LAYOUTS_CHOICES = (
    ('left',        _("Left Text Right Image")),
    ('right',       _("Right Text Left Image")),
    ('whole',       _("Only Text")),
)

LINK_TYPE_CHOICES = (
    ('link',        _("Link")),
    ('button',       _("Button")),
    ('learn-more',       _("Learn More")),
)

ITEMS_PER_ROWS_CHOICES = (
    ('12',        _("1 Item")),
    ('6',        _("2 Items")),
    ('4',        _("3 Items")),
    ('3',        _("4 Items")),
)

BOXES_PER_ROWS_CHOICES = (
    ('2', '2 Boxes per row'),
    ('3', '3 Boxes per row'),
    ('4', '4 Boxes per row'),
)

CAROUSEL_SIZE_CHOICES = (
    ('regular',     _("Regular")),
    ('full',        _("Full Screen")),
    ('condensed',   _("Condensed")),
    ('inside',   _("Inside Text")),
)

HEADER_TYPE_CHOICES = (
    ('h1',     _("H1")),
    ('h2',        _("H2")),
    ('h3',        _("H3")),
)


class DropdownChooserBlock(blocks.ChooserBlock):
    """Model chooser rendered as a dropdown (compatible with Wagtail 6 StreamField)."""

    @cached_property
    def widget(self):
        return widgets.Select()

    def get_form_state(self, value):
        return self.field.widget.format_value(
            self.field.prepare_value(self.value_for_form(value))
        )


class FormChoserBlock(DropdownChooserBlock):
    target_model = WtForm



class BaseRelatedLinkBlock(blocks.StructBlock):

    LINK_TYPE_CHOICES = (
        ('link',        _("Link")),
        ('button',       _("Button")),
        ('reverse',       _("Inverted Button")),
        ('gold',       _("Gold Button")),

    )

    title = blocks.CharBlock(label=_("Title"), icon='title')
    link_type = blocks.ChoiceBlock(
        choices=LINK_TYPE_CHOICES, required=True, label=_("Link Type"))
    new_window = blocks.BooleanBlock(
        required=False, label=_("Open link in new window"))


class ExternalLinkBlock(BaseRelatedLinkBlock):
    link = blocks.URLBlock(required=True, label=_("External link"))


class ONNILinkBlock(BaseRelatedLinkBlock):
    link = None
    link_type = None


class MenuExternalLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), icon='title')
    background_image = ImageChooserBlock(
        required=False, label=_("Background Image"))
    animation_svg = blocks.TextBlock(required=False, label=_("Animation SVG"))
    new_window = blocks.BooleanBlock(
        required=False, label=_("Open link in new window"))
    link = blocks.URLBlock(required=True, label=_("External link"))


class PageLinkBlock(BaseRelatedLinkBlock):
    link = blocks.PageChooserBlock(required=False, label=_(
        "Internal Page link (current page if empty)"), )
    hash = blocks.CharBlock(required=False)


class PhoneLinkBlock(BaseRelatedLinkBlock):
    link = blocks.CharBlock(required=True, label=_("Phone Link"))


class EmailLinkBlock(BaseRelatedLinkBlock):
    link = blocks.EmailBlock(required=True, label=_("Email Link"))


class FormLinkBlock(BaseRelatedLinkBlock):
    link = FormChoserBlock(required=True, label=_("Pop Up Form link"))


class DocumentLinkBlock(BaseRelatedLinkBlock):
    link = DocumentChooserBlock(required=True, label=_("Document"))


class NewRelatedLinksStreamBlock(blocks.StreamBlock):
    internal_page_link = PageLinkBlock(
        label=_("Internal Page Link"), icon='title')
    external_page_link = ExternalLinkBlock(
        label=_("External Page Link"), icon='title')
    phone_link = PhoneLinkBlock(label=_("Phone Link"), icon='title')
    email_link = EmailLinkBlock(label=_("Email Link"), icon='title')
    form_link = FormLinkBlock(label=_("Popup Form"), icon='title')
    doc_link = DocumentLinkBlock(label=_("Document Link"), icon='title')
    onni_link = ONNILinkBlock(label=_("ONNI Website Link"), icon='title')

    class Meta:
        icon = 'title'
        label = _("Related Links")


class NewRelatedLinksBlock(blocks.StructBlock):
    align = blocks.ChoiceBlock(choices=(('text-left', 'Left'), ('text-center', 'Center'),
                               ('text-right', 'Right')), default='text-left', label=_("Align Links"))
    description = blocks.TextBlock(
        required=False, label=_("Description"), icon='title')
    links = NewRelatedLinksStreamBlock(required=False, label=_("Links"))


class RelatedLinksBlock(blocks.StreamBlock):

    link = NewRelatedLinksStreamBlock(label=_("Link"))


class LogoBlock(blocks.StructBlock):
    logo = ImageChooserBlock(required=True, label=_("Logo"))
    link = blocks.URLBlock(required=False, label=_("Link"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['uid'] = 'logo-%s' % str(uuid.uuid4())
        # context['style'] = '{} / {}'.format(
        #     value['logo'].width,
        #     value['logo'].height
        # ) if value['logo'] else '1 / 1'
        return context


class GalleryBlock(blocks.StructBlock):

    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_tag = blocks.ChoiceBlock(
        choices=HEADER_TYPE_CHOICES, default='h2', required=True, label=_("Title Tag"))
    mode = blocks.ChoiceBlock(choices=GALLERY_MODE, default='lt-12')
    full_width = blocks.BooleanBlock(default=False, required=False)
    images = blocks.ListBlock(ImageChooserBlock, label=_("Images"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['uid'] = 'gallery-%s' % str(uuid.uuid4())

        ret = OrderedDict()
        images = value['images']
        if images:
            i = 0
            for image in images:
                ret[i] = image
                i += 1

        context['add_css'] = 'remind-{}'.format(len(ret) % 3)
        context['images'] = list(ret.items())
        return context


class RawHtmlBlock(blocks.StructBlock):
    text = blocks.TextBlock(required=True, label=_("HTML"), icon='title')


class CollectionChoserBlock(DropdownChooserBlock):
    target_model = Collection

    def value_from_form(self, value):
        if value is None or isinstance(value, self.target_model):
            return value
        else:
            if value:
                try:
                    return self.target_model.objects.get(pk=value)
                except self.target_model.DoesNotExist:
                    return None
            return None


class ImageTagChoserBlock(DropdownChooserBlock):
    target_model = Tag

    def value_from_form(self, value):
        if value is None or isinstance(value, self.target_model):
            return value
        else:
            if value:
                try:
                    return self.target_model.objects.get(pk=value)
                except self.target_model.DoesNotExist:
                    return None
            return None

    @cached_property
    def field(self):
        from taggit.models import TaggedItem
        from wagtail.images import get_image_model
        Image = get_image_model()
        return forms.ModelChoiceField(
            queryset=self.target_model.objects.filter(id__in=TaggedItem.tags_for(Image).values('id')), widget=self.widget, required=self._required,
            help_text=self._help_text)


class GalleryCollectionsItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(classname="full", label=_("Title"), icon='title')
    collection = CollectionChoserBlock(
        required=False, label=_("Gallery Collection"))
    tag = ImageTagChoserBlock(required=False, label=_("Image Tag"))


class GalleryCollectionsBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_tag = blocks.ChoiceBlock(
        choices=HEADER_TYPE_CHOICES, default='h2', required=True, label=_("Title Tag"))
    show_categories = blocks.BooleanBlock(required=False)
    show_image_title = blocks.BooleanBlock(required=False)
    mode = blocks.ChoiceBlock(choices=GALLERY_MODE, default='lt-12')
    full_width = blocks.BooleanBlock(required=False)
    theme = SnippetChooserBlock(CssTheme, required=False,)
    gallery_collections = blocks.ListBlock(
        GalleryCollectionsItemBlock(), label=_("Gallery Collections"), required=True,)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        collections = []

        ret = OrderedDict()
        id = 0
        if value['gallery_collections']:
            for item in value['gallery_collections']:
                id += 1
                if item['collection'] or item['tag']:
                    collections.append({'id': id, 'title': item['title']})
                    if item['collection']:
                        images = Image.objects.filter(
                            collection__id=item['collection'].id)
                        images = images.extra(select={
                                              'sort_order': "SELECT sort_order FROM wtadmin_wtimagesort WHERE wtadmin_wtimagesort.image_id = wagtailimages_image.id"})
                    elif item['tag']:
                        images = Image.objects.filter(tags__id=item['tag'].id)
                        images = images.extra(select={
                                              'sort_order': "SELECT sort_order FROM wtadmin_wtimagesortbytag WHERE wtadmin_wtimagesortbytag.image_id = wagtailimages_image.id and wtadmin_wtimagesortbytag.tag_id={}".format(item['tag'].id)})

                    images = images.order_by('sort_order')

                    for image in images:
                        if image.id in ret:
                            ret[image.id].cats.append(
                                {'id': id, 'sort_order': image.sort_order if image.sort_order else 0})
                        else:
                            image.cats = [
                                {'id': id, 'sort_order': image.sort_order if image.sort_order else 0}]
                            ret[image.id] = image

            ret = list(ret.items())

            # context['image_chunks_12'] = [ret[i:i + 12] for i in range(0, len(ret), 12)]
            context['add_css'] = 'remind-{}'.format(len(ret) % 3)

            context['images'] = ret
            context['collections'] = collections
            context['uid'] = 'gallery-%s' % str(uuid.uuid4())

        return context


# class InstagramTokenChoserBlock(blocks.ChooserBlock):
#     target_model=WtInstagramToken
#     widget=widgets.Select

# class InstagramThumbnailsBlock(blocks.StructBlock):
#     class Meta:
#         template='wtpages/blocks/instagram_thumbnails_block.html'

#     add_hash = blocks.CharBlock(required=False, label=_("Hash"), icon = 'title')
#     title = blocks.CharBlock(label=_("Title"), required=False, )
#     tag = blocks.CharBlock(label=_("Tag"), required=False, )
#     link = blocks.URLBlock(label=_("Link"), required=False, )
#     instagram_token = InstagramTokenChoserBlock(label=_("Instagram Token"), required=True, )
#     cols = blocks.IntegerBlock(default=5)
#     rows = blocks.IntegerBlock(default=1)
#     theme = SnippetChooserBlock(CssTheme, required=False,)

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context=parent_context)
#         context['items'] = value['instagram_token'].social_content_items.all() if value['instagram_token'] else None
#         return context


class TextBlock(blocks.StructBlock):

    PAGE_LAYOUTS_CHOICES = (
        ('left',        _("Left Text Right Image")),
        ('right',       _("Right Text Left Image")),
        ('whole',       _("Only Text")),
    )

    TITLE_TYPE_CHOICES = (
        ('default',        _("Default")),
        ('subhead',       _("Blue Subhead")),
        ('gold',       _("Gold Subhead")),
    )

    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    title_type = blocks.ChoiceBlock(
        choices=TITLE_TYPE_CHOICES, required=True, default="default", label=_("Title Type"))
    layout = blocks.ChoiceBlock(choices=PAGE_LAYOUTS_CHOICES,
                                required=True, classname="full", label=_("Text Layout"))
    # full_width = blocks.BooleanBlock(required=False, default=True)

    larger = blocks.BooleanBlock(required=False)
    spacing = blocks.BooleanBlock(required=False)
    more_spacing = blocks.BooleanBlock(required=False)
    bottom = blocks.BooleanBlock(required=False)

    theme = SnippetChooserBlock(CssTheme, required=False,)
    image = ImageChooserBlock(required=False, label=_("Image"))
    night_time_image = ImageChooserBlock(required=False)
    text_align = blocks.ChoiceBlock(
        choices=TEXT_BLOCK_ALIGN_CHOICES, required=False, label=_("Text Align"))
    text = blocks.RichTextBlock(
        classname="full", required=False, label=_("Text"))
    new_links = NewRelatedLinksBlock(
        label=_("Related Links"), required=False, )


# class ImageChooserBlockThemed(blocks.StructBlock):
#     class Meta:
#         template='wtpages/blocks/themed_image.html'

#     image = ImageChooserBlock(classname="full", required=False, label=_("Image"))
#     theme = SnippetChooserBlock(CssTheme, required=False,)


# class AddressBlock(blocks.StructBlock):
#     class Meta:
#         template='wtpages/blocks/address_block.html'

#     title = blocks.CharBlock(classname="full", required=False, label=_("Title"), icon = 'title')
#     #show_more_info = blocks.BooleanBlock(required=False)
#     theme = SnippetChooserBlock(CssTheme, required=False,)
#     #text = blocks.RichTextBlock(classname="full", required=False, label=_("Text"))
#     #left_image = ImageChooserBlock(classname="full", required=False, label=_("Left Image"))
#     #right_image = ImageChooserBlock(classname="full", required=False, label=_("Right Image"))
#     #new_links = NewRelatedLinksBlock(label=_("Related Links"), required=False, )


# class BoxesItemBlock(blocks.StructBlock):
#     image = ImageChooserBlock(classname="full", required=False, label=_("Image"))
#     image_caption = blocks.CharBlock(classname="full", required=False, label=_("Image Caption"), )
#     title = blocks.CharBlock(classname="full", required=False, label=_("Title"), icon = 'title')
#     text = blocks.RichTextBlock(classname="full", required=False, label=_("Text"))
#     new_links = NewRelatedLinksBlock(label=_("Related Links"), required=False, )


# class BoxesBlock(blocks.StructBlock):
#     BOXES_IMAGE_SIZE_CHOICES=(
#         ('866x866', 'Square'),
#         ('866x539', 'Horizontal'),
#         ('500x700', 'Vertical'),
#     )
#     class Meta:
#         template='wtpages/blocks/boxes_block.html'
#     title = blocks.CharBlock(classname="full", required=False, label=_("Title"), icon = 'title')
#     boxes_per_row = blocks.ChoiceBlock(choices=LINKED_BOXES_PER_ROWS_CHOICES, label=_("Boxes Per Row"), default=3)
#     image_size = blocks.ChoiceBlock(choices=BOXES_IMAGE_SIZE_CHOICES, label=_("Boxes Image Size"), default='866x866')
#     theme = SnippetChooserBlock(CssTheme, required=False,)
#     boxes = blocks.ListBlock(BoxesItemBlock, label=_("Boxes"), required=False, )

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context=parent_context)
#         context['uid'] = 'boxes-block-%s' % str(uuid.uuid4())
#         return context


class CarouselBlock(blocks.StructBlock):

    TEXT_LAYOUT_CHOICES = (
        ('left', _("Left")),
        ('center', _("Center")),
        ('right', _("Right")),
    )

    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_tag = blocks.ChoiceBlock(
        choices=HEADER_TYPE_CHOICES, default='h2', required=True, label=_("Title Tag"))
    text = blocks.TextBlock(required=False, label=_("Text"), icon='text')
    text_layout = blocks.ChoiceBlock(
        default='left', choices=TEXT_LAYOUT_CHOICES, label=_("Text Layout"), icon='title')
    show_controls = blocks.BooleanBlock(
        required=False, label=_("Show Arrows"), icon='title')
    full_width = blocks.BooleanBlock(
        required=False, label=_("Full Width"), icon='title')
    show_tint = blocks.BooleanBlock(
        required=False, label=_("Show Tint"), icon='title')
    theme = SnippetChooserBlock(CssTheme, required=False,)
    image_size = blocks.ChoiceBlock(
        choices=CAROUSEL_SIZE_CHOICES, default='insidetext', label=_("Image Size"), )
    images = blocks.ListBlock(
        ImageChooserBlock, label=_("Images"), required=False, )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['uid'] = 'carousel-block-%s' % str(uuid.uuid4())
        return context


class ImageBlock(blocks.StructBlock):

    image = ImageChooserBlock(label=_("Image"))


class VideoChoserBlock(DropdownChooserBlock):
    target_model = Video


class VideoBlock(blocks.StructBlock):

    # VIDEO_SIZE_CHOICES = (
    #     ('regular',        _("Regular")),
    #     ('fullwidth',        _("Full Width")),
    #     ('fullscreen',      _("Full Screen")),
    # )

    # add_hash = blocks.CharBlock(required=False, label=_("Hash"), icon = 'title')
    title = blocks.CharBlock(required=False, label=_("Title"), icon='title')
    video = VideoChoserBlock(required=True, label=_("Video"))
    poster = ImageChooserBlock(
        classname="full", required=False, label=_("Image"))
    show_controls = blocks.BooleanBlock(default=False, required=False)
    # show_mute_button = blocks.BooleanBlock(default=False, required=False)
    # video_size = blocks.CharBlock(default='regular', choices=VIDEO_SIZE_CHOICES)
    theme = SnippetChooserBlock(CssTheme, required=False,)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value['video']:
            context['transcodes'] = []
            items = value['video'].transcodes.exclude(
                processing=True).filter(error_message__exact='')
            if items:
                for item in items:
                    context['transcodes'].append(
                        {'url': item.url, 'mime': 'video/%s' % item.media_format})
        return context


class SiteMapBlock(blocks.StructBlock):
    pass


class InteractiveMapChoserBlock(DropdownChooserBlock):
    target_model = InteractiveMaps


class InteractiveMapBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    mobile_title = blocks.CharBlock(
        classname="full", required=False, label=_("Mobile Title"), icon='title')
    tab_name = blocks.CharBlock(
        required=False, label=_("Tab Name"), icon='title')
    interactive_map = InteractiveMapChoserBlock(
        required=True, label=_("Interactive Map"), icon='title')
    full_width = blocks.BooleanBlock(
        required=False, label=_("Full Width"), icon='title')
    show_legend = blocks.BooleanBlock(
        required=False, label=_("Show Legend"), icon='title')
    theme = SnippetChooserBlock(CssTheme, required=False,)


class InteractiveMapTabsBlock(blocks.StructBlock):
    maps = blocks.ListBlock(InteractiveMapBlock, label=_("Interactive Maps"))


class PlacesChoserBlock(DropdownChooserBlock):
    target_model = InteractiveGoogleMaps


class PlacesBlock(blocks.StructBlock):

    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    # text_align = blocks.ChoiceBlock(choices=TEXT_BLOCK_ALIGN_CHOICES, required=False, label=_("Text Align"))
    # text = blocks.RichTextBlock(classname="full", required=False, label=_("Text"))
    instance = PlacesChoserBlock(required=True, label=_(
        "Neighborhood Map Instance"), icon='title')


class ImagesAndTextGalleryItemImage(blocks.StructBlock):

    DECOR_CHOICES = (
        ('top-left',        _("Top Left Corner")),
        ('top-right',        _("Top Right Corner")),
        ('bottom-left',      _("Bottom Left Corner")),
    )

    image = ImageChooserBlock(label=_("Image"))
    decor = blocks.ChoiceBlock(
        choices=DECOR_CHOICES, required=False, label=_("Decor Triangle"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['uid'] = str(uuid.uuid4())
        return context


class ImagesAndTextGalleryItemTextText(blocks.StructBlock):

    title = blocks.CharBlock(label=_("Title"), icon='title')
    text = blocks.RichTextBlock(label=_("Text"))


class ImagesAndTextGalleryItemText(blocks.StructBlock):

    items = blocks.StreamBlock([
        ('image', ImagesAndTextGalleryItemImage(label=_("Image"), icon='title')),
        ('text', ImagesAndTextGalleryItemTextText(
            label=_("Text Box"), icon='title')),
    ], label=_('Items'), min_num=2, max_num=2)


class ImagesAndTextGalleryItemTextImage(blocks.StructBlock):
    items = blocks.StreamBlock([
        ('image', ImagesAndTextGalleryItemImage(label=_("Image"), icon='title')),
        ('text', ImagesAndTextGalleryItemText(
            label=_("Info Box (Text + Image)"), icon='title')),
    ], label=_('Items'), min_num=2, max_num=2)


class ImagesAndTextGalleryRow(blocks.StructBlock):
    boxes = blocks.StreamBlock([
        ('image_box', ImagesAndTextGalleryItemImage(
            label=_("Image Box"), icon='title')),
        ('image_text_box', ImagesAndTextGalleryItemTextImage(
            label=_("Image & Info Box"), icon='title')),
    ], label=_('Boxes'), min_num=2, max_num=2)


class ImagesAndTextGalleryBlock(blocks.StructBlock):

    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_tag = blocks.ChoiceBlock(
        choices=HEADER_TYPE_CHOICES, default='h2', required=True, label=_("Title Tag"))

    # boxes = blocks.StreamBlock([
    #     ('image_box', ImagesAndTextGalleryItemImage(label=_("Image Box"), icon = 'title')),
    #     ('image_text_box', ImagesAndTextGalleryRow(label=_("Images & Text Box"), icon = 'title')),
    # ], label=_('Boxes') )

    rows = blocks.ListBlock(ImagesAndTextGalleryRow(
        label=_("Section")), label=_("Sections"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['rel'] = 'gallery-%s' % str(uuid.uuid4())
        return context


class AboutOnniCollageImage(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), icon='title')
    image = ImageChooserBlock(label=_("Image"))


class AboutOnniCollageImageGroup(blocks.StructBlock):
    images = blocks.ListBlock(AboutOnniCollageImage(
        label=_("Image")), label=_("Images"), min_num=2, max_num=2)


class AboutOnniCollageBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), icon='title')
    image_groups = blocks.ListBlock(AboutOnniCollageImageGroup(
        label=_("Image Group")), label=_("Image Groups"), min_num=3, max_num=3)


class SharedBlocksBlock(blocks.StructBlock):
    shared_blocks = SnippetChooserBlock('towers.SharedPageBlocks')


class FeatuesBlockItemsList(blocks.StructBlock):
    text = blocks.RichTextBlock(classname="full", label=_("Text"))
    force_new_column = blocks.BooleanBlock(required=False)


class FeatuesBlockItems(blocks.StructBlock):
    title = blocks.CharBlock(classname="full", label=_("Title"), icon='title')
    # gallerytext = blocks.RichTextBlock(classname="full", label=_("Text"))
    items = blocks.ListBlock(FeatuesBlockItemsList(
        label=_("Item")), label=_("Items"))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['uid'] = 'feature-%s' % str(uuid.uuid4())
        return context


class FeaturesBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    features = blocks.ListBlock(
        FeatuesBlockItems, required=False, label=_("Featues"))
    theme = SnippetChooserBlock(CssTheme, required=False,)
    new_links = NewRelatedLinksBlock(
        label=_("Related Links"), required=False, )


class TowerPlansBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    theme = SnippetChooserBlock(CssTheme, required=False,)


class TowerViewsBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    text = blocks.RichTextBlock(required=False, label=_("Text"))
    penthouses_only = blocks.BooleanBlock(required=False)
    theme = SnippetChooserBlock(CssTheme, required=False,)


class InfoBlockItems(blocks.StructBlock):
    title = blocks.CharBlock(classname="full", label=_("Title"), icon='title')
    text = blocks.RichTextBlock(classname="full", label=_("Text"))


class InfoBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        classname="full", required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    items = blocks.ListBlock(InfoBlockItems, required=False, label=_("Items"))
    theme = SnippetChooserBlock(CssTheme, required=False,)


class OnniLogoBlock(blocks.StructBlock):
    theme = SnippetChooserBlock(CssTheme, required=False,)


class ContactBlockItem(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), icon='title')
    text = blocks.RichTextBlock(required=False, label=_("Text"))


class ContactBlock(blocks.StructBlock):
    # title = blocks.CharBlock(classname="full", required=False, label=_("Title"), icon = 'title')
    # title_2 = blocks.TextBlock(required=False, label=_("More Title Lines"), icon = 'title')
    # theme = SnippetChooserBlock(CssTheme, required=False,)
    items = blocks.ListBlock(ContactBlockItem, label=_("Sections"))


class PenthousesBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label=_("Title"), icon='title')
    title_2 = blocks.TextBlock(required=False, label=_(
        "More Title Lines"), icon='title')
    text = blocks.RichTextBlock(required=False, label=_("Text"))
    # boxes_per_row = blocks.ChoiceBlock(choices=BOXES_PER_ROWS_CHOICES, label=_("Boxes Per Row"), default=3)


class HashBlock(blocks.StructBlock):
    hash = blocks.CharBlock()


stream_field_blocks = [
    # ('header', HeaderBlock(label=_("Header"), icon='pilcrow')),
    ('paragraph', TextBlock(label=_("Text"), icon='pilcrow')),
    ('hash', HashBlock(label=_("Hash"), icon='pilcrow')),

    ('image', ImageBlock(label=_("Image"))),
    # ('address', AddressBlock(label=_("Address"), icon='pilcrow')),
    ('form', FormChoserBlock(required=False, label=_("Form"), icon='pilcrow')),
    # ('instagramthumbnails', InstagramThumbnailsBlock(required=False, label=_("Instagram Thumbnails"), icon='pilcrow')),
    ('gallery', GalleryBlock(required=False, label=_("Gallery"), icon='pilcrow')),
    ('gallery_collections', GalleryCollectionsBlock(
        required=False, label=_("Gallery (Collections)"), icon='pilcrow')),
    ('texts_and_images_gallery', ImagesAndTextGalleryBlock(
        required=False, label=_("Text & Images Gallery"), icon='pilcrow')),

    # ('boxes', BoxesBlock(required=False, label=_("Boxes"), icon='pilcrow')),
    # ('text_boxes', TextBoxesBlock(required=False, label=_("Text Boxes"), icon='pilcrow')),
    # ('separator', blocks.StaticBlock(template='wtpages/blocks/separator_block.html', label=_("Separator"), icon='pilcrow')),
    ('carousel', CarouselBlock(label=_("Carousel"), icon='pilcrow')),
    ('video', VideoBlock(label=_("Video"), icon='pilcrow')),
    # ('faq_block', FaqBlock(label=_("Faq"), icon='pilcrow')),
    # ('team', TeamBlock(label=_("Team"), icon='pilcrow')),
    # ('rooms', RoomThumbnailsBlock(label=_("Room Thumbnails"), icon='pilcrow')),
    # ('rooms_preview', RoomsPreviewBlock(label=_("Rooms Preview"), icon='pilcrow')),
    # ('events', EventThumbnailsBlock(label=_("Event Thumbnails"), icon='pilcrow')),
    # ('press', PressBlock(label=_("Press"), icon='pilcrow')),
    #
    ('onni_logo', OnniLogoBlock(label=_("ONNI Logo With Link"), icon='pilcrow')),
    ('info', InfoBlock(label=_("Info"), icon='pilcrow')),

    ('features',     FeaturesBlock(label=_("Features"), icon='pilcrow')),
    ('shared_blocks', SharedBlocksBlock(label=_("Shared Blocks"), icon='pilcrow')),

    ('interactive_map', InteractiveMapBlock(
        label=_("Interactive Map"), icon='pilcrow')),
    ('interactive_map_tabks', InteractiveMapTabsBlock(
        label=_("Interactive Map Tabs"), icon='pilcrow')),

    ('places', PlacesBlock(label=_("Neighborhood Map"), icon='pilcrow')),

    ('tower_plans', TowerPlansBlock(label=_("Tower Plans"), icon='pilcrow')),
    ('tower_views', TowerViewsBlock(label=_("Tower Views"), icon='pilcrow')),
    ('penthouses_widget', PenthousesBlock(label=_("Penthouses"), icon='pilcrow')),

    ('about_collage', AboutOnniCollageBlock(
        label=_("About ONNI Collage"), icon='pilcrow')),
    ('contact', ContactBlock(label=_("Contact"), icon='pilcrow')),


    ('site_map', SiteMapBlock(label=_("Site Map"), icon='pilcrow')),
    ('raw_html', RawHtmlBlock(label=_("Raw HTML"), icon='pilcrow')),
]
