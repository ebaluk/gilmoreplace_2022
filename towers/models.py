import os
import sys
from django.core.files.storage import default_storage as storage
from django.utils.translation import gettext_lazy as _
from django.db.models import signals
from wagtail.images import get_image_model, get_image_model_string
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from willow.image import Image as Willow_Image
from PIL import Image as PIL_Image
from io import BytesIO
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from wtpages.models import *


Image = get_image_model()

@register_snippet
class TowerBedroomTypes(models.Model):
    class Meta:
        ordering = ('sort_order',)
        verbose_name = _('Tower Bedroom Type')
        verbose_name_plural = _('Tower Bedroom Types')

    title = models.TextField(blank=False)
    title_zh_hans = models.TextField(blank=False, verbose_name=_('Simplified Chinese Title'))
    title_zh_hant = models.TextField(blank=False, verbose_name=_('Traditional Chinese Title'))
    sort_order = models.IntegerField(default=0, db_index=True)
    visible = models.BooleanField(default=True)

    panels = [
        MultiFieldPanel([
                FieldPanel('title'),
                FieldPanel('title_zh_hans'),
                FieldPanel('title_zh_hant'),
                FieldPanel('sort_order'),
                FieldPanel('visible'),
            ],
            heading=_("Basic"),
        ),
    ]

    def __str__(self):
        return str(self.title)

@register_snippet
class TowerPenthouseTypes(models.Model):
    class Meta:
        ordering = ('sort_order',)
        verbose_name = _('Tower Penthouse Type')
        verbose_name_plural = _('Tower Penthouse Types')

    title = models.TextField(blank=False)
    title_zh_hans = models.TextField(blank=False, verbose_name=_('Simplified Chinese Title'))
    title_zh_hant = models.TextField(blank=False, verbose_name=_('Traditional Chinese Title'))
    sort_order = models.IntegerField(default=0, db_index=True)
    visible = models.BooleanField(default=True)

    panels = [
        MultiFieldPanel([
                FieldPanel('title'),
                FieldPanel('title_zh_hans'),
                FieldPanel('title_zh_hant'),
                FieldPanel('sort_order'),
                FieldPanel('visible'),
            ],
            heading=_("Basic"),
        ),
    ]

    def __str__(self):
        return str(self.title)

@register_snippet
class SharedPageBlocks(models.Model):   
    title = models.TextField(blank=False)
    stream_field = StreamField(stream_field_blocks, use_json_field=True)
    panels = [
        MultiFieldPanel([
                FieldPanel('title'),                
               
            ],
            heading=_("Basic"),     

        ),      
        FieldPanel('stream_field'),
    ]
    def __str__(self):
        return self.title

class TowerPlanFloorPlateImageRenditionImage(Orderable):
    rendition = ParentalKey('TowerPlanFloorPlateImageRendition', related_name='images')
    image = models.ImageField(upload_to='images/floorplates')

    def del_image(self):
        self.image.delete()

def pre_delete_floor_plate_image(sender, instance, **kwargs):
    instance.del_image()

signals.pre_delete.connect(pre_delete_floor_plate_image, sender=TowerPlanFloorPlateImageRenditionImage)

class TowerPlanFloorPlateImageRendition(ClusterableModel):
    image_hash = models.CharField(max_length=40)        
    tower_plan = models.ForeignKey('TowerPlan', related_name='+', on_delete=models.CASCADE)


class TowerPlan(Orderable):
    tower = ParentalKey('Tower', related_name='plans')
    title = models.CharField(max_length=255)  
    pdf = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    floorplates_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    floorplan_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')    
    bedrooms = models.ForeignKey(TowerBedroomTypes, null=False, blank=False, on_delete=models.PROTECT, related_name='+')
    penthouse_type = models.ForeignKey(TowerPenthouseTypes, null=True, blank=True, on_delete=models.SET_NULL, related_name='+', help_text=_('For Penthouses Stream Field Block'))
    interiors = models.CharField(max_length=255, null=True, blank=True,)  
    exteriors = models.CharField(max_length=255, null=True, blank=True,)   
    total_sqft = models.CharField(max_length=255, null=True, blank=True,)   

    sold = models.BooleanField(default=False)

    # floorplates_images = StreamField([
    #     ('image', ImageChooserBlock(label=_('Image'))),
    # ], null=True, blank=True)

    @cached_property
    def floorplates_image_renditions(self):
        if self.floorplates_image:
            try:
                rend = TowerPlanFloorPlateImageRendition.objects.get(tower_plan=self)                
            except TowerPlanFloorPlateImageRendition.DoesNotExist:
                rend = TowerPlanFloorPlateImageRendition(
                    tower_plan=self
                )
            
            if not rend.image_hash == self.floorplates_image.file_hash:
                if rend.images.all():
                    rend.images.all().delete()

                rend.image_hash = self.floorplates_image.file_hash
                
                img = PIL_Image.open(storage.open(self.floorplates_image.file.name))
                img = img.resize((640, 360), PIL_Image.LANCZOS)

                i = 0
                for row in range(0, 2):
                    for col in range(0, 4):
                        x = col * 159
                        y = row * 160 + 46
                        new_i = img.crop((x, y, x+159, y+160))

                        if new_i.getbbox():
                            i += 1

                            tmpIO = BytesIO()
                            new_i.save(tmpIO, format='PNG')
                            tmpFile = InMemoryUploadedFile(
                                tmpIO, None, "{}-{}-{}.png".format(rend.image_hash, self.id, i), 
                                'image/png', sys.getsizeof(tmpIO), None)

                            rend.images.create(
                                sort_order=i,
                                image=tmpFile
                            )
                rend.save()            
            return rend.images.all()

        else:
            return []                

    

    panels = [
        FieldPanel('title'),
        FieldPanel('pdf'),
        FieldPanel('floorplates_image'),        
        # StreamFieldPanel('floorplates_images'),
        FieldPanel('floorplan_image'),        
        FieldPanel('bedrooms'),
        FieldPanel('penthouse_type'),        
        FieldPanel('interiors'),
        FieldPanel('exteriors'),
        FieldPanel('total_sqft'),        
        FieldPanel('sold'),
        
    ]
    
class TowerView(Orderable):
    tower = ParentalKey('Tower', related_name='views')
    title = models.CharField(max_length=255)      
    image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    penthouse_view = models.BooleanField(default=False, help_text=_('For View Widget, when Penthouses Only selected'))

    panels = [
        FieldPanel('title'),
        FieldPanel('image'),
        FieldPanel('penthouse_view'),        
    ]


class Tower(ClusterableModel):
    class Meta:
        verbose_name = _("Towers")       
    
    title = models.CharField(max_length=255)        
        
    def __str__(self):
        return self.title
    
    panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),            
            
        ],heading=_('Basic')),

        MultiFieldPanel([InlinePanel('plans'),],heading=_('Plans'),classname="collapsible collapsed"),
        MultiFieldPanel([InlinePanel('views'),],heading=_('Views'),classname="collapsible collapsed"),
    ]
    


class TowersIndexPage(WtBasePage):
    class Meta:
        verbose_name = _("Towers Index Page")    

    is_tower_index_page = True    

    subpage_types = ['TowerPage']    

    content_panels = [      
    
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),                      
            FieldPanel('theme'),
        ],heading=_('Basic')),

        WtBasePage.hero_panels,       
        
    ]
        

class TowerPage(StandardPage):
    class Meta:
        verbose_name = _("Tower Page")    

    parent_page_types = ['TowersIndexPage']    
    subpage_types = ['TowerInternalPage']
    

    tower_type = models.ForeignKey('towers.Tower', on_delete=models.PROTECT, related_name='+', verbose_name=_('Tower Type'))

    icon_desktop = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    icon_mobile = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = [      
    
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),                      
            FieldPanel('tower_type'),
            FieldPanel('icon_desktop'),
            FieldPanel('icon_mobile'),
            FieldPanel('theme'),
        ],heading=_('Basic')),

        MultiFieldPanel([
            FieldPanel('hero_title'),                        
            #FieldPanel('hero_text'),
            FieldPanel('hero_text_align'),        
            #StreamFieldPanel('hero_links'),            
            
            VideoChooserPanel('hero_video'),
            FieldPanel('hero_video_loop'),
        
            InlinePanel('hero_images', label=_('Hero Image')),        
        
        ], _('Hero Banner')),
        
        
        FieldPanel('stream_field'),
        
    ]

    
class TowerInternalPage(StandardPage):
    class Meta:
        verbose_name = _("Towers Internal Page")    

    parent_page_types = ['TowerPage']        
    subpage_types = []

    

    content_panels = [      
    
        MultiFieldPanel([
            FieldPanel('title', classname="full title"),                      
            FieldPanel('theme'),
        ],heading=_('Basic')),

        MultiFieldPanel([
            FieldPanel('hero_title'),                        
            #FieldPanel('hero_text'),
            FieldPanel('hero_text_align'),        
            #StreamFieldPanel('hero_links'),            
            
            VideoChooserPanel('hero_video'),
            FieldPanel('hero_video_loop'),
        
            InlinePanel('hero_images', label=_('Hero Image')),        
        
        ], _('Hero Banner')),
        
        
        FieldPanel('stream_field'),
        
    ]

        