from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from towers.models import TowerPenthouseTypes, TowerPlan

DATA = [
    {
        'title': '2 Bed', 
        't2p': {
            '7': ['PH1', 'PH2', 'SPH A', 'SPH A1', 'SPH A2', 'SPH A3', 'SPH A4', 'SPH A5'],
            '9': ['PH1', 'SPH A', 'SPH A1', 'SPH A2'],
        }
    },
    {
        'title': '2 Bed + Den',
        't2p': {
            '7': ['PH3', 'PH4', 'PH5', 'SPH B', 'SPH B1'],
            '8': ['PH3', 'PH5', 'SPH B'],
            '9': ['PH2', 'PH3', 'PH4', 'PH5', 'SPH B', 'SPH B1', 'SPH B2', 'SPH B3'],
        }
    },    
    {
        'title': 'Jr. 3 Bed',
        't2p': {
            '7': ['SPH C'],
            '8': ['SPH C', 'SPH C1'],            
        }
    },
    {
        'title': '3 Bed',
        't2p': {            
            '8': ['PH1', 'SPH D'],            
        }
    },
    {
        'title': '3 Bed + Den',
        't2p': {
            '7': ['PH6', 'SPH E'],
            '8': ['PH6', 'SPH E', 'SPH E1'],
            '9': ['PH6', 'SPH E'],
        }
    }
]

class Command(BaseCommand):

    def handle(self, *args, **options):

        sort_order = 0
        for item in DATA:
            print(item['title'])
            print('-----------')
            pt = TowerPenthouseTypes(
                title=item['title'],
                sort_order=sort_order
            )
            pt.save()
            sort_order += 1

            for tw_id, t2p in item['t2p'].items():
                print('Tower: ', tw_id)
                for t2p_item in t2p:
                    print('Tower Plan: ', t2p_item)
                    tower_plan = TowerPlan.objects.get(tower__id=int(tw_id), title=t2p_item)
                    tower_plan.penthouse_type = pt
                    tower_plan.save(force_update=True)


