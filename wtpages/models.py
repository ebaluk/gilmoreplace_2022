import math

from django.db import models
from django.utils.functional import cached_property

from django.http.response import HttpResponsePermanentRedirect

from wagtail.fields import RichTextField, StreamField

from wagtail.models import Page, Orderable

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel

from wagtail.snippets.models import register_snippet

from wagtail.search import index

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey


from django.utils import translation
from django.http import HttpResponseRedirect

# locale
from django.utils.translation import gettext_lazy as _

# WT
# from django.conf import settings as system_settings

# from wtforms.models import WtFormLinkField

from wagtailvideos.edit_handlers import VideoChooserPanel
from wagtailvideos.models import Video

from wagtail.images import get_image_model_string

from .blocks import stream_field_blocks
from .csstheme import CssTheme

from .blocks import (
    PageLinkBlock, ExternalLinkBlock, PhoneLinkBlock,
    EmailLinkBlock, FormLinkBlock, DocumentLinkBlock,
    LogoBlock
)
from .headless import NextHeadlessPreviewMixin


class LanguageRedirectionPage(NextHeadlessPreviewMixin, Page):
    # parent_page_types = ['wagtailcore.Page']
    # subpage_types = ['pages.StandardPage','pages.StandardIndexPage']
    parent_page_types = []

    def serve(self, request):
        language = translation.get_language_from_request(request)
        return HttpResponseRedirect(self.url + language + '/')


class CarouselItem(models.Model):
    image = models.ForeignKey(get_image_model_string(
    ), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    panels = [
        FieldPanel('image'),
    ]

    class Meta:
        abstract = True


# jjs codes, type kit and similar stuff
# @register_snippet
class JsCodePlacement(models.Model):
    page = ParentalKey('wagtailcore.Page', related_name='js_code_placements')
    jscode = models.ForeignKey(
        'wtpages.JsCode', related_name='+', on_delete=models.CASCADE)


DOC_POS = (
    ('doc_end', 'End of document (before </body>)'),
    ('doc_beg', 'Beginning of document (after <body>)'),
    ('head',    'Head (inside <head>)'),
)


class JsCodePage(Orderable):
    page = models.ForeignKey('wagtailcore.Page', null=True,
                             blank=True, on_delete=models.SET_NULL, related_name='+')
    jscode = ParentalKey('JsCode', related_name='pages')
    panels = [
        PageChooserPanel('page'),
    ]


class JsCodeExcludePage(Orderable):
    page = models.ForeignKey('wagtailcore.Page', null=True,
                             blank=True, on_delete=models.SET_NULL, related_name='+')
    jscode = ParentalKey('JsCode', related_name='exclude_pages')
    panels = [
        PageChooserPanel('page'),
    ]


@register_snippet
class JsCode(ClusterableModel):
    title = models.TextField(blank=False)
    doc_position = models.CharField(
        max_length=10, choices=DOC_POS, default='doc_end')
    text = models.TextField(blank=False)
    panels = [
        # FieldPanel('title'),
        # FieldPanel('text'),
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('doc_position'),
            FieldPanel('text'),
        ],
            heading=_("All Pages JavaScript code"),
            # heading=_("JavaScript код для всех страниц"),
            # classname="collapsible collapsed"
        ),
        MultiFieldPanel([InlinePanel('pages'),], heading=_(
            'Pages'), classname="collapsible"),
        MultiFieldPanel([InlinePanel('exclude_pages'),], heading=_(
            'Exclude Pages'), classname="collapsible"),

    ]

    def __str__(self):
        return self.title


class WtBasePageHeroImages(Orderable):
    visible = True
    page = ParentalKey('WtBasePage', related_name='hero_images')
    image = models.ForeignKey(get_image_model_string(
    ), on_delete=models.CASCADE, related_name='+')
    panels = [
        FieldPanel('image'),
    ]


class WtBasePage(NextHeadlessPreviewMixin, Page):

    HERO_TEXT_ALIGN = (
        ('left', _('Left')),
        ('right', _('Right')),
    )

    COLOR_THEME_CHOICES = (
        ('default', _('Default')),
        ('white', _('White')),
    )

    is_creatable = False

    seo_keywords = models.TextField(verbose_name=_('SEO keywords'), blank=True)
    theme = models.ForeignKey('wtpages.CssTheme', null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='+', verbose_name=_('Theme'))

    show_in_sitemap = models.BooleanField(default=True)
    show_navbar = models.BooleanField(default=False)

    open_graph_image = models.ForeignKey(get_image_model_string(
    ), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    hero_video = models.ForeignKey(
        Video, null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_('Hero Video'))
    hero_video_loop = models.BooleanField(default=False)
    hero_title = models.CharField(max_length=255, null=True, blank=True)
    hero_text_align = models.CharField(
        max_length=10, choices=HERO_TEXT_ALIGN, default='left')
    hero_text = models.TextField(blank=True, verbose_name=_("Hero Text"))
    hero_links = StreamField([
        ('internal_page_link', PageLinkBlock(
            label=_("Internal Page Link"), icon='title')),
        ('external_page_link', ExternalLinkBlock(
            label=_("External Link"), icon='title')),
        ('phone_link', PhoneLinkBlock(label=_("Phone Link"), icon='title')),
        ('email_link', EmailLinkBlock(label=_("Email Link"), icon='title')),
        ('form_link', FormLinkBlock(label=_("Popup Form"), icon='title')),
        ('doc_link', DocumentLinkBlock(label=_("Document Link"), icon='title')),
    ], null=True, blank=True, use_json_field=True)

    hero_mobile_half_height = models.BooleanField(
        default=True, verbose_name=_('Half height on mobile'))

    color_theme = models.CharField(
        max_length=20, choices=COLOR_THEME_CHOICES, default='default')

    logos_banner = StreamField([
        ('logo', LogoBlock(label=_("Logo"), icon='title')),
    ], null=True, blank=True, use_json_field=True)

    @cached_property
    def hero_video_transcodes(self):
        ret = None
        if self.hero_video:
            items = self.hero_video.transcodes.exclude(
                processing=True).filter(error_message__exact='')
            if items:
                ret = []
                for item in items:
                    ret.append(
                        {'url': item.url, 'mime': 'video/%s' % item.media_format})
        return ret

    @cached_property
    def hero_carousel_images(self):
        return self.hero_images.all()

    @cached_property
    def navbar_items(self):
        return self.get_parent().get_children().live().in_menu()

    @cached_property
    def logos_banner_items(self):
        original_list = list(self.logos_banner)
        original_list_len = len(original_list)
        if not original_list_len or original_list_len >= 11:
            return self.logos_banner

        target_length = 11
        repetitions = math.ceil(target_length / original_list_len)
        # Repeat the list the required number of times and trim the excess
        repeated_list = (original_list * repetitions)[:target_length]

        return repeated_list

    # def serve(self, request, *args, **kwargs):
    #     from towers.models import TowerPage
    #     request.tower_page = None
    #     if isinstance(self, TowerPage):
    #         request.tower_page = self
    #     else:
    #         request.tower_page = TowerPage.objects.ancestor_of(self).live().first()
    #     return super(WtBasePage, self).serve(request, *args, **kwargs)

    hero_panels = MultiFieldPanel([
        FieldPanel('hero_title'),
        FieldPanel('hero_text'),
        FieldPanel('hero_text_align'),
        FieldPanel('hero_mobile_half_height'),

        FieldPanel('hero_links'),

        VideoChooserPanel('hero_video'),
        FieldPanel('hero_video_loop'),

        InlinePanel('hero_images', label=_('Hero Image')),

        FieldPanel('logos_banner'),




    ], _('Hero Banner'))

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('show_navbar'),
            FieldPanel('color_theme'),
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('seo_keywords'),
            FieldPanel('show_in_sitemap'),
            FieldPanel('open_graph_image'),
        ], _('Common page configuration')),
    ]


class URLPage(NextHeadlessPreviewMixin, Page):
    class Meta:
        verbose_name = _("URL Page")
    link_external = models.URLField(blank=True, null=True)
    external = models.BooleanField(
        default=False, help_text='Open link in a new window')

    link_page = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    link_document = models.ForeignKey(
        'wagtaildocs.Document', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    def serve(self, request, *args, **kwargs):
        if self.link:
            return HttpResponsePermanentRedirect(self.link)
        return super(URLPage, self).serve(request, *args, **kwargs)

    content_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="title"),
            FieldPanel('link_external'),
            PageChooserPanel('link_page'),
            FieldPanel('link_document'),
            FieldPanel('external'),
        ], heading=_('Basic')),
    ]
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('slug'),
            # FieldPanel('seo_title'),
            # FieldPanel('search_description'),
            # FieldPanel('seo_keywords'),
        ], _('Common page configuration')),
    ]


class StandardPage(WtBasePage):
    class Meta:
        verbose_name = _("Text Page")

    redirect_to_first_child = models.BooleanField(
        default=False, help_text='Show the first child page instead of showing this one')

    stream_field = StreamField(stream_field_blocks, null=True, blank=True, use_json_field=True)

    def serve(self, request, *args, **kwargs):
        if self.redirect_to_first_child:
            c = self.get_children().live().first()
            if c:
                return c.specific.serve(request, *args, **kwargs)
        return super(StandardPage, self).serve(request, *args, **kwargs)

    content_panels = [

        MultiFieldPanel([
            FieldPanel('title', classname="full title"),
            FieldPanel('theme'),
        ], heading=_('Basic')),

        WtBasePage.hero_panels,

        FieldPanel('stream_field'),

    ]

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('show_navbar'),
            FieldPanel('color_theme'),
            FieldPanel('redirect_to_first_child'),
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('seo_keywords'),
            FieldPanel('show_in_sitemap'),
            FieldPanel('open_graph_image'),
        ], _('Common page configuration')),
    ]
