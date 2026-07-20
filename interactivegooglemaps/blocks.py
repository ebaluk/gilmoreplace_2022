from wagtail import blocks
from django.utils.translation import gettext_lazy as _


class PlaceBlock(blocks.StructBlock):    
    class Meta:
        template='interactivegooglemaps/blocks/place_block.html'
    title = blocks.CharBlock(label=_("Title"), icon = 'title')                    
    latitude = blocks.CharBlock()
    longitude = blocks.CharBlock()
    address = blocks.TextBlock(required=False)
    url = blocks.URLBlock(required=False)
   