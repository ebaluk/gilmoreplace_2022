from django.utils.translation import gettext_lazy as _
from wtpages.models import *
from wtpages.blocks import (
    PageLinkBlock, ExternalLinkBlock, PhoneLinkBlock, 
    EmailLinkBlock, FormLinkBlock, DocumentLinkBlock,    
)


class PromoBoxItemPage(Orderable):
    page = models.ForeignKey('wagtailcore.Page', null=True,
                             blank=True, on_delete=models.SET_NULL, related_name='+')
    promo = ParentalKey('PromoBoxItem', related_name='pages')
    panels = [
        PageChooserPanel('page'),
    ]


class PromoBoxItem(ClusterableModel):
    MODE_CHOICES = (
        ('default', _('Text and Image')),
        ('image', _('Image Only')),
        ('text', _('Text Only')),
    )
    title = models.CharField(max_length=255)
    body = RichTextField(blank=True, verbose_name=_('Text'))
    image = models.ForeignKey(get_image_model_string(), null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='+', verbose_name=_('Image'))
    mode = models.CharField(choices=MODE_CHOICES, default='default', max_length=20)

    links_stream_field = StreamField([
            ('internal_page_link', PageLinkBlock(label=_("Internal Page Link"), icon = 'title')),
            ('external_page_link',ExternalLinkBlock(label=_("External Page Link"), icon = 'title')),
            ('phone_link',PhoneLinkBlock(label=_("Phone Link"), icon = 'title')),
            ('email_link',EmailLinkBlock(label=_("Email Link"), icon = 'title')),
            ('form_link',FormLinkBlock(label=_("Popup Form"), icon = 'title')),
            ('doc_link',DocumentLinkBlock(label=_("Document Link"), icon = 'title')),
        ], null=True, blank=True, use_json_field=True)

    show_logo = models.BooleanField(default=True)
    smaller_popup = models.BooleanField(default=False)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @cached_property
    def image_ratio(self):
        return (self.image.height / self.image.width) * 100 if self.image and self.image.width else None     

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title', classname="full title"),
                FieldPanel('body'),
                FieldPanel('image'),
                FieldPanel('mode'),
                FieldPanel('show_logo'),
                FieldPanel('smaller_popup'),                
                FieldPanel('visible'),
            ],
            heading="Basic",
        ),
        MultiFieldPanel([InlinePanel('pages'), ], heading=_(
            'Show On Pages'), classname="collapsible"),
        MultiFieldPanel([
            FieldPanel('links_stream_field')            
         ], heading=_(
            'Related Links'), classname="collapsible"),
    ]

    def __unicode__(self):
        return self.title
