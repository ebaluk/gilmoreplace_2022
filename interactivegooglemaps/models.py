from django import forms
from modelcluster.models import ClusterableModel
from django.utils.translation import gettext_lazy as _

from wtpages.models import *
from .blocks import PlaceBlock 

class InteractiveGoogleMapPlaces(Orderable):        
    page = ParentalKey('InteractiveGoogleMaps', related_name='place_groups')
    title = models.CharField(max_length=255)  
    color = models.CharField(max_length=20)
    places = StreamField([
        ('places',  PlaceBlock(label=_("Places"), icon='pilcrow')),        
    ], use_json_field=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('color', widget=forms.TextInput(attrs={'class': 'colorPicker'})),
        FieldPanel('places'),        
    ]



class InteractiveGoogleMaps(ClusterableModel):
    class Meta:
        verbose_name = _("Neighborhood Maps")       
    
    title = models.CharField(max_length=255)    
    latitude = models.CharField(max_length=255, verbose_name=_('Main Location latitude'))    
    longitude = models.CharField(max_length=255, verbose_name=_('Main Location longitude'))    
    
    def __str__(self):
        return self.title
    
    panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),
            FieldPanel('latitude', classname="full title"),
            FieldPanel('longitude', classname="full title"),
        ],heading=_('Basic')),

        MultiFieldPanel([InlinePanel('place_groups'),],heading=_('Place Groups'),classname="collapsible"),
    ]
    
