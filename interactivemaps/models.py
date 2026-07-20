
from django.utils.safestring import mark_safe
from modelcluster.models import ClusterableModel
from django.utils.translation import gettext_lazy as _
import math
from wtpages.models import *

class InteractiveMapsLayoutPoints(Orderable):
    page = ParentalKey('InteractiveMaps', related_name='points')
    title = models.CharField(max_length=255, )
    body = RichTextField(blank=True, verbose_name=_('Text'),)
    left = models.FloatField(default=0, verbose_name=_('Left, %'))
    top = models.FloatField(default=0, verbose_name=_('Top, %'))
    visible = models.BooleanField(blank=True, default=1)
    
    radius = 10
    
    @property
    def style(self):
        w = self.page.layout_image.width 
        h = self.page.layout_image.height
        return 'left: {:.15f}%; top: {:.15f}%;'.format(self.left, self.top) if w and h else ''

    
    panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        # ImageChooserPanel('image'),
        FieldPanel('left'),
        FieldPanel('top'),
        FieldPanel('visible'),
    ]
    
    
  


class InteractiveMaps(ClusterableModel):
    class Meta:
        verbose_name = _("Interactive Maps")       
    
    title = models.CharField(max_length=255)    
    layout_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+', help_text=mark_safe('<span class="btn-layout-image-points-wrapper">Click <a id="btn-layout-image-points" href="#">HERE</a> for Points visual editor.</span>'))

    
    def __str__(self):
        return self.title
    
    @property
    def layout_image_points(self):
        return self.points.filter(visible=True).order_by('sort_order')        


    @property
    def legend(self):
        items = self.layout_image_points
        i = 0
        for item in items:
            i+=1
            item.idx = i

        items_len = len(items)
        cnt = math.ceil(items_len / 2)
        return [items[i:i + cnt] for i in range(0, items_len, cnt)]
    
    @property
    def style(self):
        return 'padding-top: {:.15%}'.format((self.layout_image.height/self.layout_image.width)) if self.layout_image and self.layout_image.width and self.layout_image.height else ''
    
    panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),            
            FieldPanel('layout_image', ),            
        ],heading=_('Basic')),

        MultiFieldPanel([InlinePanel('points'),],heading=_('Floor Plan Image Points'),classname="collapsible collapsed"),
    ]
    
