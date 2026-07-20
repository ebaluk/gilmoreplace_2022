from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

SITEMAP_CHOICES = (
    ('generic',     _("Use Generic Sitemap")),
    ('custom',       _("Use Uploaded Sitemap")),    
)

DEFAULT_ROBOTS = "User-agent: *\nDisallow: /admin/"

@register_setting
class WtSitemap(BaseSiteSetting):
    class Meta:
        verbose_name = 'Sitemap'
    type = models.CharField(max_length=50, default='generic', choices=SITEMAP_CHOICES, blank=False)
    file = models.FileField(blank=True, null=True, upload_to='sitemaps', verbose_name=_('Sitemap file'))
    robots = models.TextField(blank=True, default="User-agent: *\nDisallow: /admin/", help_text=DEFAULT_ROBOTS, verbose_name=_('robots.txt'))    
    
    panels = [
        MultiFieldPanel([
                FieldPanel('type'),
                FieldPanel('file'),
                FieldPanel('robots'),
            ],
            #heading=_('Common'),
            #classname="collapsible collapsed"
        ),
              
    ]

