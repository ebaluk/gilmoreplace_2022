from django.http import Http404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wtpages.models import *
from wtpages.blocks import (
    PageLinkBlock, ExternalLinkBlock, PhoneLinkBlock, 
    EmailLinkBlock, FormLinkBlock, DocumentLinkBlock,    
)
from wtpages.headless import NextHeadlessPreviewMixin


class HomePage(NextHeadlessPreviewMixin, Page):
    class Meta:
        verbose_name = _("Website Root Page")
        
    subpage_types = ['LanguageRootPage']
        
    def serve(self, request):
        # This will only return a language that is in the LANGUAGES Django setting
        language = translation.get_language_from_request(request)
        page = None
        try:            
            page = LanguageRootPage.objects.get(language_code=language.lower())
        except LanguageRootPage.DoesNotExist:
            page = LanguageRootPage.objects.first()

        if not page:
            raise Http404

        return HttpResponseRedirect(page.url)

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
        ], _('Common page configuration')),
    ]

    content_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),
        ],heading=_('Basic')),
    ]


class LanguageRootPageFooterSocialLinks(Orderable):
    page = ParentalKey('LanguageRootPage', related_name='footer_social_links')    
    title = models.CharField(max_length=255)    
    fontawesome_icon = models.CharField(max_length=50, null=True, blank=True, help_text=_("Set any icon listed there https://fontawesome.com/v4.7.0/icons/") )
    link = models.URLField()
    new_window = models.BooleanField(default=True)

    panels = [      
        FieldPanel('title'),
        FieldPanel('fontawesome_icon'),
        FieldPanel('link'),
        FieldPanel('new_window'),                
    ]


class LanguageRootPage(StandardPage):
    class Meta:
        verbose_name = _("Language Root Page")

    is_root_page = True
    
        
    #parent_page_types = ['LanguageRootPage']
    #subpage_types = ['wtmenus.MenuCategoryPage']
    
    footer_legal = RichTextField(null=True, blank=True)
    contact_page_link = models.ForeignKey('wtpages.StandardPage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    penthouse_collections_page = models.ForeignKey('wtpages.StandardPage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    promo_box = models.ForeignKey('wtpromobox.PromoBoxItem', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

        
    page_404_title = models.CharField(max_length=255)
    page_404_text = RichTextField(blank=True, verbose_name = _("Page Not Found Text"))
    page_404_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))    
    email = models.EmailField(blank=True)

    language_code = models.CharField(max_length=20, choices=settings.LANGUAGES, default='en-us')

    
    

    footer_links = StreamField([
        ('internal_page_link', PageLinkBlock(label=_("Internal Page Link"), icon = 'title')),
        ('external_page_link',ExternalLinkBlock(label=_("External Page Link"), icon = 'title')),
        ('phone_link',PhoneLinkBlock(label=_("Phone Link"), icon = 'title')),
        ('email_link',EmailLinkBlock(label=_("Email Link"), icon = 'title')),
        ('form_link',FormLinkBlock(label=_("Popup Form"), icon = 'title')),
        ('doc_link',DocumentLinkBlock(label=_("Document Link"), icon = 'title')),
    ], null=True, blank=True, use_json_field=True)

    
    @property
    def page_404_images(self):
        return [{'image': self.page_404_image, 'visible': True,},] if self.page_404_image else None  

    @property
    def lang_translated(self):
        return settings.LANGUAGES_TRANSLATIONS[self.language_code]
        

    content_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),
            FieldPanel('language_code'),
            FieldPanel('phone'),
            FieldPanel('email'),
            PageChooserPanel('contact_page_link'),
            PageChooserPanel('penthouse_collections_page'),            
            FieldPanel('promo_box'),            
            FieldPanel('footer_legal'),            
            FieldPanel('theme'),
        ],heading=_('Basic')),     
    
        WtBasePage.hero_panels,

        MultiFieldPanel([            
            FieldPanel('footer_links'),           
        ],heading=_('Footer Links'),classname="collapsible collapsed"),

        MultiFieldPanel([
            InlinePanel('footer_social_links'),
        ],heading=_('Footer Social Links'),classname="collapsible collapsed"),

        MultiFieldPanel([            
            FieldPanel('page_404_title'),
            FieldPanel('page_404_text'),
            FieldPanel('page_404_image'),
        ],heading=_('Page Not Found (404)'), classname="collapsible collapsed"),

        
        FieldPanel('stream_field'),
        

    ]

    
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('show_in_menus'),            
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('seo_keywords'),           
            FieldPanel('open_graph_image'),            
        ], _('Common page configuration')),
    ] 

   