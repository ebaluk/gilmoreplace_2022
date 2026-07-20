from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

#locale
from django.utils.translation import gettext_lazy as _
from wagtail.images import get_image_model_string

@register_setting
class WtPageMeta(BaseSiteSetting):
    class Meta:
        verbose_name = _("Page Meta")
    site_name = models.CharField(max_length=255)
    default_title = models.CharField(max_length=255, blank=True, null=True )
    default_description = models.TextField(blank=True, null=True )
    default_keywords = models.TextField(blank=True, null=True )
    default_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    fb_app_id = models.CharField(max_length=255, blank=True, null=True, verbose_name = _("Facebook APP ID"))
    
    panels = [
        MultiFieldPanel([
                FieldPanel('site_name'),
                FieldPanel('default_title'),
                FieldPanel('default_description'),
                FieldPanel('default_keywords'),              
                FieldPanel('fb_app_id'),
                FieldPanel('default_image'),
            ],
            heading=_('Common'),
        ),
    ]
