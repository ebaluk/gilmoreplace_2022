import re
import json
from django.utils.functional import cached_property
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel


class CssThemeImages(Orderable):
    POSITION_CHOICES = (
        ('top_left', 'Top Left'),
        ('top_middle', 'Top Middle'),
        ('top_right', 'Top Right'),
        ('right_middle', 'Right Middle'),
        ('bottom_right', 'Bottom Right'),
        ('bottom_middle', 'Bottom Middle'),
        ('bottom_left', 'Bottom Left'),
        ('left_middle', 'Left Middle'),
    )
    theme = ParentalKey('CssTheme', related_name='images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )

    position = models.CharField(default='left', max_length=20, choices=POSITION_CHOICES )
    #width = models.IntegerField(default=150)
    background_size = models.CharField(blank=True, null=True, max_length=255, )    
    background_position = models.CharField(blank=True, null=True, max_length=255, )    

    scroll_animate = models.BooleanField(default=False)

    inside_container = models.BooleanField(default=False)

    
    @property
    def render_css(self):
        p = re.compile( "\{id\}")
        return p.sub( '#decor-%d-%d' % (self.theme.pk, self.pk), self.css)

    
    panels = [
        
        FieldPanel('image'),

        FieldPanel('position'),
        #FieldPanel('width'),
        FieldPanel('background_size'),
        FieldPanel('background_position'),        
        FieldPanel('inside_container'),
        FieldPanel('scroll_animate'),       
        
        
    ]
    
    

@register_snippet
class CssTheme(ClusterableModel):
    class Meta:
        verbose_name = _('Css Theme')
        verbose_name_plural=_('Css Themes')
        ordering = ('title',)        
        
    title = models.CharField(max_length=255)

    color = models.CharField(max_length=255, blank=True)
    background = models.CharField(max_length=255, blank=True)
    title_color = models.CharField(max_length=255, blank=True)
    title_background = models.CharField(max_length=255, blank=True)
    
    css_class = models.CharField(max_length=255, blank=True, null=True)

    css = models.TextField(verbose_name = _('Css'), blank=True, help_text=_('Raw CSS. There are NO validation, please be careful. {theme} should precede any selector.'))

    def __str__(self):
        return self.title

    def render_theme(self):
        res = '';
        try:
            if self.id:
                th = '.themed-'+ str(self.id)
                th = th.lower()
                if self.color:
                    res += th+' *{color: '+self.color+"}\n"
                if self.background:
                    res += th+'{background-color: '+self.background+"}\n"
                if self.title_color:
                    res += th+' .page-header.inside *, ' +th+' .page-header.insidetext *{color: '+self.title_color+" !important}\n"
                if self.title_background:
                    res += th+' h1,'+th+' h2,'+th+' h3,'+th+' h4{background-color: '+self.title_color+"}\n"

                if self.css:
                    css = self.css
                    p = re.compile( "\{theme\}")
                    res += p.sub( th, css)
        except:
            pass

        return res


    panels = [
        MultiFieldPanel([
                FieldPanel('title', classname=""),
                FieldPanel('color'),
                FieldPanel('background'),
                FieldPanel('title_color'),
                FieldPanel('title_background'),
                FieldPanel('css', classname=""),
                FieldPanel('css_class'),
                
            ],
            heading=_("Basic"),
        ),

        MultiFieldPanel([InlinePanel('images'),],heading=_('Images'),classname="collapsible collapsed"),            
    ]    