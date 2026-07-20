import sys
import os

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage as storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from PIL import Image
from io import BytesIO

config = {
    'shortcut icon': [16, 32, 48, 128, 192],
    'touch-icon': [192],
    'icon': [192],
    'apple-touch-icon': [57, 72, 114, 144, 180],
    'apple-touch-icon-precomposed': [57, 72, 76, 114, 120, 144, 152, 180],
}

config = getattr(settings, 'FAVICON_CONFIG', config)

def pre_delete_image(sender, instance, **kwargs):
    instance.del_image()



class WtFavicon(models.Model):

    title = models.CharField(max_length=100)
    faviconImage = models.ImageField(upload_to="favicon")
    isFavicon = models.BooleanField(default=True)
    
    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title', classname="full title"),
                FieldPanel('faviconImage',),
                FieldPanel('isFavicon',),                
            ],
            heading="Basic",
        ),
    ]

    class Meta:
        verbose_name = 'Favicon'
        verbose_name_plural = 'Favicons'

    def get_favicons(self):
        favicons = []
        for rel in config:
            for size in config[rel]:
                favicons.append(self.get_favicon(size, rel))
        return favicons

    def __str__(self):
        return self.faviconImage.name

    def get_absolute_url(self):
        return "%s" % self.faviconImage.name

    def del_image(self):
        self.faviconImage.delete()

    def get_favicon(self, size, rel, update=False):
        """
        get or create a favicon for size, rel(attr) and uploaded favicon
        optional:
            update=True
        """
        
            
        fav, _ = WtFaviconImg.objects.get_or_create(faviconFK=self, size=size, rel=rel)
        if update and fav.faviconImage:
            fav.del_image()
        if self.faviconImage and not fav.faviconImage:
            
            fn, ex = os.path.splitext(self.faviconImage.name)
            bn = os.path.basename(fn)
            
            tmp = Image.open(storage.open(self.faviconImage.name))
            tmp.thumbnail((size, size), Image.ANTIALIAS)

            tmpIO = BytesIO()
            tmp.save(tmpIO, format='PNG')
            tmpFile = InMemoryUploadedFile(
                tmpIO, None, 'fav-%s-%s.png' % (size, bn ), 
                'image/png', sys.getsizeof(tmpIO), None)

            fav.faviconImage = tmpFile
            fav.save()
        return fav

    def save(self, *args, **kwargs):
        update = True

        if self.isFavicon:
            for n in WtFavicon.objects.exclude(pk=self.pk):
                n.isFavicon = False
                n.save()

        super(WtFavicon, self).save(*args, **kwargs)

        if self.faviconImage:
            for rel in config:
                for size in config[rel]:
                    self.get_favicon(size=size,rel=rel, update=update)


        #make sure default favicon is set
        self.get_favicon(size=32, rel='shortcut icon')
        


class WtFaviconImg(models.Model):
    faviconFK = models.ForeignKey(WtFavicon, on_delete=models.CASCADE)
    size = models.IntegerField()
    rel = models.CharField(max_length=250, null=True)
    faviconImage = models.ImageField(upload_to='favicon')

    def del_image(self):
        self.faviconImage.delete()

from django.db.models import signals
#from django.db.models.signals import pre_delete
#from django.dispatch.dispatcher import receiver

signals.pre_delete.connect(pre_delete_image, sender=WtFavicon)
signals.pre_delete.connect(pre_delete_image, sender=WtFaviconImg)
