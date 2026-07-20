from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.utils.translation import gettext_lazy as _
from wagtail.images.models import Image
from django.conf import settings
import os
import datetime
import requests
from django.db import transaction
from wagtail.models import Collection
from modelcluster.models import ClusterableModel, ParentalKey

COLLECTION_NAME = 'Social Feed'

class SocialContentItem(models.Model):
    page = ParentalKey('WtInstagramToken', related_name='social_content_items')
    feed_datetime = models.DateTimeField(blank=True,null=True)
    feed_user = models.CharField(max_length=255,blank=True,null=True)
    feed_text = models.TextField(blank=True,null=True)
    feed_status = models.CharField(max_length=40,blank=True,null=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name = _("Image")
    )

    feed_thumbnail = models.TextField(blank=True,null=True)
    feed_dsc = models.CharField(max_length=255,blank=True,null=True)
    feed_id = models.CharField(max_length=255,blank=True,null=True)
    feed_link = models.TextField(blank=True,null=True)
    timezone = models.CharField(max_length=255,blank=True,null=True)

    invalid = models.BooleanField(default=True)

class WtInstagramToken(ClusterableModel):
    class Meta:
        verbose_name = _("Instagram Token")        
    name = models.CharField(max_length=255, null=False,blank=False, help_text='You will be able to select this Token for the Social Media Page Items')
    token = models.CharField(max_length=255, null=True,blank=True,)
   
    def __str__(self):
        return self.name

    def get_image(self, folder, url, title, tags, fn=None):
        if not fn:
            fn = url.split('/')[-1]
            fn = fn.split('?')[0]
        fn = os.path.join(folder, fn)
        
        try:
            
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, folder))
            
            if not os.path.isfile( os.path.join(settings.MEDIA_ROOT, fn) ):
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(os.path.join(settings.MEDIA_ROOT, fn), 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                
            try:
                image = Image.objects.get(
                    file = fn,
                    title=title,
                )
            except Image.DoesNotExist:
                try:
                    theCollection = Collection.objects.get(name = COLLECTION_NAME)
                except Collection.DoesNotExist:
                    theCollection = Collection.get_first_root_node().add_child(instance = Collection(
                        name = COLLECTION_NAME
                    ))
                    theCollection.save()
    
                image = Image(title=title)
                image.file = fn
                image.collection_id = theCollection.id
                image.save()
                if tags:
                    image.tags.add(*tags)
                    image.save()
    
            return image
                
        except:
            return None    


    @transaction.atomic
    def fetch_in(self):      
        
        print('Fetching data from Instagram: %s' % self.name)
        SocialContentItem.objects.filter(page=self).delete()
        
        url = "https://graph.instagram.com/me/media/?fields=id,caption,media_type,media_url,username,timestamp,permalink,thumbnail_url&access_token=" + self.token
        req = requests.get(url)
        data = req.json()
        for item in data["data"]:
            folder = 'original_images/social/in'
            image = self.get_image(folder,  item["thumbnail_url"] if 'thumbnail_url' in item else item["media_url"], "Instagram Image", None)
            SocialContentItem(
                page = self,
                feed_dsc = '',                        
                feed_datetime = datetime.datetime.strptime(item["timestamp"], '%Y-%m-%dT%H:%M:%S%z'),
                feed_user = item["username"][:255] if "username" in item else "",
                feed_text = item["caption"] if "caption" in item else "",
                feed_image = image,
                feed_thumbnail = item["media_url"],
                feed_id = item['id'],
                feed_link = item['permalink'],
                timezone = '',                
            ).save(force_insert=True)

    @transaction.atomic
    def clear_all(self):        
        SocialContentItem.objects.filter(page=self).delete()

    panels = [
        MultiFieldPanel([
                FieldPanel('name', classname="full title"),                
            ],
            heading=_('Common'),          
        ),

        MultiFieldPanel([
                FieldPanel('token', ),
                
            ],
            heading=_('Instagram Token And Status (read only)'),          
        ),
    ]
