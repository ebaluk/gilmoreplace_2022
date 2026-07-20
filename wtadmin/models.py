from django import forms
from django.db import models

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel

#from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
#
#from wagtail.documents.edit_handlers import DocumentChooserPanel

#locale
from django.utils.translation import gettext_lazy as _
from wagtail.images import get_image_model_string

@register_setting
class WtSettings(BaseSiteSetting):

    caption = models.CharField(max_length=255)
    logo = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    smtp_host = models.CharField(max_length=255, null=True,blank=True,)
    smtp_user = models.CharField(max_length=255, null=True,blank=True,)
    smtp_pass = models.CharField(max_length=255, null=True,blank=True,)
    
    #reservations_box_text = RichTextField(blank=True, verbose_name = _("Reservations Box Text"))
    
    
    #page_404_text = RichTextField(blank=True, verbose_name = _("Page Not Found Text"))
    #page_404_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    
    #footer_text = RichTextField(blank=True, default='')

    # footer_signup_title = models.CharField(max_length=255, null=True, blank=True)
    # footer_signup_text = RichTextField(blank=True, default='')
    # footer_signup_page_link = models.ForeignKey('wtpages.StandardPage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    
    
    # header_signup_form = models.ForeignKey('wtforms.WtForm', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    

    # top_promo_line = RichTextField(blank=True, )
    # show_top_promo_line = models.BooleanField(default=False)    

    ga_view_id = models.IntegerField(default=0)
    

    
    # address = models.TextField(blank=True)    
    # phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))    
    # email = models.EmailField(blank=True)
    # map_code = models.TextField(blank=True, verbose_name=_('Map'))    

    # show_language_switch = models.BooleanField(default=True)    
    # show_login = models.BooleanField(default=True)    
    
    # map_style = models.TextField(blank=True, verbose_name=_('Map Style'), help_text='Go to the https://snazzymaps.com/explore find required theme and copy/paste it here')
    
    # @property
    # def page_404_images(self):
    #     return [{'image': self.page_404_image, 'visible': True,},] if self.page_404_image else None  

    panels = [
        MultiFieldPanel([
                FieldPanel('caption'),
                FieldPanel('logo'),
            ],
            heading=_('Admin Branding'),
            #classname="collapsible collapsed"
        ),     
        
        MultiFieldPanel([                        
            FieldPanel('ga_view_id'),          
        ],heading=_('Google Analytics')),

        # MultiFieldPanel([                        
        #     FieldPanel('map_style'),
        # ],heading=_('Google Map API Styles')),
        
        MultiFieldPanel([
                FieldPanel('smtp_host'),
                FieldPanel('smtp_user'),
                FieldPanel('smtp_pass'),
            ],
            heading=_('Email settings'),
            #classname="collapsible collapsed"
        ),

        # MultiFieldPanel([
        #     FieldPanel('top_promo_line'),
        #     FieldPanel('show_top_promo_line'),
        # ],heading=_('Top Promo Line')),    
              
        #FieldPanel('reservations_box_text'),
        # FieldPanel('page_404_text'),
        # ImageChooserPanel('page_404_image'),
        
        # FieldPanel('footer_text'),
        
        #FieldPanel('header_signup_form'),
        
    ]

class WtImageSort(models.Model):
    image = models.OneToOneField(
        get_image_model_string(),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+'
    )
    sort_order = models.IntegerField(default=0)


class WtImageSortByTag(models.Model):
    class Meta:
        unique_together = (
            ('image', 'tag'),
        )

    image = models.ForeignKey(get_image_model_string(), null=False, blank=False, on_delete=models.CASCADE, related_name='+')
    tag = models.ForeignKey('taggit.Tag', null=False, blank=False, on_delete=models.CASCADE, related_name='+')
    sort_order = models.IntegerField(default=0)    
    

