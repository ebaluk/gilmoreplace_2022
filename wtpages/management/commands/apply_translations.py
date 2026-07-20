import os
import json
import re
import uuid
#from django.db import transaction
from django.core.management.base import BaseCommand
from wagtail.rich_text import RichText
from wthomepage.models import LanguageRootPage
from wtpages.models import StandardPage, WtBasePage
from towers.models import SharedPageBlocks, TowersIndexPage, TowerInternalPage
from interactivemaps.models import InteractiveMaps
from wtforms.models import WtForm


translations = {    
    'zh-hant': 'tc',    
    'zh-hans': 'sc',    
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'locales')

TITLE_RE = r"(.*)\<span\>(.*)<\/span\>"

shared_features = {
    'tc': 5,
    'sc': 7,
}

shared_amenities = {
    'tc': 4,
    'sc': 6,
}

forms = {
    'tc': 2,
    'sc': 3,
}

class Command(BaseCommand):

    data = None
    lang_code = None
    language_root_page = None

    def set_block_title(self, block, title):
        #More <br> <span>Of Everything <br> You Can Imagine</span>
        matches = re.match(TITLE_RE, title, re.IGNORECASE)
        if matches:
            block.value['title'] = matches.group(1).replace('<br>', '')
            block.value['title_2'] = matches.group(2).replace('<br>', '\n')
        else:
            block.value['title'] = title
            

    def set_text_block(self, block, title, text=None, text_field_name='text'):
        self.set_block_title(block, title)                  
        if text:           
            block.value[text_field_name] = RichText('<p>{}</p>'.format(text))        
            


    def convert_shared_amenities(self):        
        instance = SharedPageBlocks.objects.get(id=shared_amenities[self.lang_code])        
        data = self.data['amenities']
        self.set_text_block(
            instance.stream_field[0],
            data['title'],
            data['copy'],
        )        


        self.set_block_title(
            instance.stream_field[1],
            data['sitemaps'][0]['tab'],            
        )        

        map = InteractiveMaps.objects.get(title__iexact='Private Wellness Centre ({})'.format(self.lang_code))
        i = 0
        for point in map.points.all():
            point.title = data['sitemaps'][0]['list'][i]            
            point.save()
            i += 1            
        

        self.set_block_title(
            instance.stream_field[2],
            data['sitemaps'][1]['tab'],            
        )        

        map = InteractiveMaps.objects.get(title__iexact='Unrivaled Outdoor Spaces ({})'.format(self.lang_code))
        i = 0
        for point in map.points.all():
            point.title = data['sitemaps'][1]['list'][i]            
            point.save()
            i += 1        

        i = 0
        for section in instance.stream_field[3].value['rows']:            
            for box in section['boxes']:
                if box.block_type == 'image_text_box':
                    for item in box.value['items']:
                        if item.block_type == 'text':
                            for text_item in item.value['items']:
                                if text_item.block_type == 'text':
                                    self.set_text_block(
                                        text_item,
                                        data['featured'][i]['title'],
                                        data['featured'][i]['copy'],                                        
                                    )
                                    i += 1

        instance.save()




    def convert_discovery_interactive(self):                
        data = self.data['discover']['vision']['sitemap']['hotspots']
        
        map = InteractiveMaps.objects.get(title__iexact='Discover Map ({})'.format(self.lang_code))
        i = 0
        for point in map.points.all():            
            point.title = data[i]['title']
            point.body = '<p>{}</p>'.format(data[i]['copy'])
            point.save()
            i += 1            


    def convert_shared_features(self):
        instance = SharedPageBlocks.objects.get(id=shared_features[self.lang_code])
        self.data['homes']['features']['content'][0]
        self.set_text_block(
            instance.stream_field[0],
            self.data['homes']['features']['content'][0]['title'],
            self.data['homes']['features']['content'][0]['copy'],
        )        
        self.set_block_title(
            instance.stream_field[1], 
            self.data['homes']['features']['content'][1]['title']
        )

        if 'new_links' in instance.stream_field[1].value and instance.stream_field[1].value['new_links']:            
            instance.stream_field[1].value['new_links']['links'][0].value['title'] = self.data['homes']['features']['content'][1]['button']        

        i = 0
        for block in instance.stream_field[1].value['features']:
            item_data = self.data['homes']['features']['features'][i]
            block['title'] = item_data['title']
            text = []
            if 'sections' in item_data:
                for section in item_data['sections']:
                    text.append('<h3>{}</h3>'.format(section['title']))
                    for list in section['list']:
                        text.append('<ul>')
                        if isinstance(list, dict):
                            text.append('<li>{}<ul><li>'.format(list['title']))
                            text.append('</li><li>'.join(list['items']))
                            text.append('</li></ul></li>')
                        else:
                            text.append('<li>{}</li>'.format(list))
                        text.append('</ul>')    
            else:
                text.append('<ul><li>')
                text.append('</li><li>'.join(item_data['list']))
                text.append('</li></ul>')


            block['text'] = RichText("".join(text))

            i += 1

        instance.save()    


    


    def convert_homes(self):
        for lp in TowersIndexPage.objects.descendant_of(self.language_root_page):
            lp.title = self.data['menu'][1]['title']
            lp.hero_title = self.data['menu'][1]['title']
            lp.save_revision().publish()

            for page in lp.get_children():
                page = page.specific
                page.title = '{} Gilmore Place'.format(page.tower_type.title)
                page.hero_title = self.data['menu'][1]['title']
                lp.save_revision().publish()

                i = 0
                for sub_page in page.get_children():
                    sub_page = sub_page.specific                            
                    sub_page.title = self.data['menu'][1]['submenu'][i]['title']
                    sub_page.hero_title = self.data['menu'][1]['title']                            

                    if sub_page.slug == 'views':                                                                    
                        self.set_block_title(
                            sub_page.stream_field[0], 
                            title=self.data['homes']['views']['title'],
                        )                        
                        sub_page.save_revision().publish()                                

                    i += 1
        

    def convert_commercial(self):
        page = StandardPage.objects.descendant_of(self.language_root_page).get(slug='commercial')
        data = self.data['commercial']
        page.title = data['title']
        page.hero_title = data['title']
        page.save_revision().publish()                                

        menu_data = self.data['menu'][2]

        i = 0
        for sub_page in page.get_children():
            sub_page = sub_page.specific
            sub_page.title = menu_data['submenu'][i]['title']
            sub_page.hero_title = data['title']            
            block = sub_page.stream_field[3]
            self.set_text_block(
                block,
                data['cta']['title'],
                data['cta']['copy'],
            )
            if 'new_links' in block.value and block.value['new_links']:            
                block.value['new_links']['links'][0].value['title'] = data['cta']['button']        


            subpage_data = data[sub_page.slug]
            self.set_text_block(
                sub_page.stream_field[0],
                subpage_data['title'],
                subpage_data['copy'],
            )

            block = sub_page.stream_field[1]            
            block.value['title'] = subpage_data['stats']['title'].replace('<br>', ' ')
            block.value['title_2'] = subpage_data['stats']['subtitle'].replace('<br>', ' ')

            j = 0
            for block in block.value['items']:                
                block['title'] = subpage_data['stats']['list'][j]['title']                
                block['text'] = RichText('<p>{}</p>'.format(subpage_data['stats']['list'][j]['copy']))
                j += 1


            i += 1    

            sub_page.save_revision().publish()

            
                
    def convert_gallery(self):
        page = StandardPage.objects.descendant_of(self.language_root_page).get(slug='gallery')
        data = self.data['gallery']
        page.title = data['title']
        page.hero_title = data['title']
        page.save_revision().publish()                                

        i = 0
        for sub_page in page.get_children():
            sub_page = sub_page.specific
            sub_page.title = data['tabs'][i]
            sub_page.hero_title = data['title']            
            block = sub_page.stream_field[0]
            self.set_block_title(
                block,
                data['instruction'],                
            )
            i += 1
            sub_page.save_revision().publish()                                
        
        

    def convert_about(self):
        page = StandardPage.objects.descendant_of(self.language_root_page).get(slug='about-onni')
        data = self.data['about']
        page.title = data['banner']['title']
        page.hero_title = data['banner']['title']
        
        block = page.stream_field[0]
        self.set_text_block(
            block,
            data['title'],
            data['copy'],
        )
        
        block = page.stream_field[1]        
        block.value['title'] = data['cta']['copy']        

        page.save_revision().publish()

    
    def convert_contact(self):
        page = StandardPage.objects.descendant_of(self.language_root_page).get(slug='contact-us')
        data = self.data['contact']
        page.title = self.data['menu'][5]['title']
        page.hero_title = self.data['menu'][5]['title']
        
        block = page.stream_field[0]
        item = block.value['items'][0]
        item['title'] = data['inquiries']

        item = block.value['items'][1]
        item['title'] = data['presentation-centre']
        text = [
            '<p>{}<p>'.format(data['address']),
            '<p>{}<p>'.format(data['hours']),
            '<p>{}<p>'.format(data['hours-except']),
            '<p>{}<p>'.format(data['hours2']),            
        ]
        item['text'] = RichText(''.join(text))

        item = block.value['items'][2]
        item['title'] = data['register']
        page.save_revision().publish()    


    def convert_form(self):    
        form = WtForm.objects.get(id=forms[self.lang_code])
        data = self.data['contact']['form']

        
        i = 0
        for field in form.form_fields.all():
            if 0 == i:
                title = data['first-name']
            elif 1 == i:
                title = data['last-name']    
            elif 2 == i:
                title = data['email']        
            elif 3 == i:
                title = data['phone']        
            elif 4 == i:
                title = data['city']        
            elif 5 == i:
                title = data['country']        
            elif 6 == i:
                title = data['realtor']['label']
            elif 7 == i:
                title = data['hear']['label']
            elif 8 == i:
                title = data['consent']    

            title = title.replace(' *', '')
            field.label = field.placeholder = title         
            field.save()

            i += 1

        
        form.submit_button_title = data['button']        

        form.save()


    
       
       
    def handle(self, *args, **options):

        # for item in SharedPageBlocks.objects.all():
        #     item.title = item.title + ' - copy'
        #     item.id = None
        #     item.save()


        for language_root_page in LanguageRootPage.objects.live():           

            if language_root_page.language_code in translations:

                self.language_root_page = language_root_page                    
                self.lang_code = translations[language_root_page.language_code]
            
                trans_file = os.path.join(DATA_DIR, '{}.json'.format(self.lang_code))
                
                with open(trans_file, 'r') as f:
                    self.data = json.loads(f.read())

                
                #self.convert_shared_features()

                #self.convert_shared_amenities()

                #self.convert_commercial()

                #self.convert_gallery()

                #self.convert_about()

                #self.convert_contact()

                #self.convert_form()

                self.convert_discovery_interactive()
                

                
                
                # print(data['home'])
                # page = language_root_page
                # page.hero_title = data['home']['banner']['title']
                # page.hero_text = data['home']['banner']['subtitle'].replace('<br/>', '\n')
                # for block in page.hero_links:                                        
                #     if 'external_page_link' == block.block_type:
                #         block.value['title'] = data['home']['banner']['button']
                # page.save()        


                # Discover
                # print(data['discover'])
                # page = StandardPage.objects.descendant_of(language_root_page).get(slug='discover')
                # page.hero_title = data['discover']['title']          
                # for block in page.stream_field:                                        
                #     if 'paragraph' == block.block_type:
                #         self.set_text_block(block, 
                #             title=data['discover']['vision']['title'],
                #             text=data['discover']['vision']['copy'],
                #         )                        
      
                # page.save()        

                



                    
                    # lp.hero_title = data['menu'][1]['title']
                    # lp.title = data['menu'][1]['title']
                    # lp.hero_title = data['menu'][1]['title']
                    # lp.save()
                    # lp.save_revision().publish()

                    


                    # page = TowerInternalPage.objects.descendant_of(lp).get(slug='plans')
                    # page.title = data['menu'][1]['submenu'][0]
                    # page.hero_title = data['menu'][1]['title']
                    # page.save()

                    # page = TowerInternalPage.objects.descendant_of(lp).get(slug='views')
                    # page.title = data['menu'][1]['submenu'][1]
                    # page.hero_title = data['menu'][1]['title']
                    # page.save()

                    # page = TowerInternalPage.objects.descendant_of(lp).get(slug='features')
                    # page.title = data['menu'][1]['submenu'][2]
                    # page.hero_title = data['menu'][1]['title']
                    # page.save()

                    # page = TowerInternalPage.objects.descendant_of(lp).live().get(slug='amenities')
                    # page.title = data['menu'][1]['submenu'][3]
                    # page.hero_title = data['menu'][1]['title']
                    # page.save()







