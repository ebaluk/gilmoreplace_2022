import re
from django.core.management.base import BaseCommand, CommandError
from towers.models import Tower

class Command(BaseCommand):

    def handle(self, *args, **options):

        for tower in Tower.objects.all():
            for tower_plan in tower.plans.all():
                
                interiors = re.sub('[,\s]*', '', tower_plan.interiors)
                exteriors = re.sub('[,\s]*', '', tower_plan.exteriors)

                # print(tower_plan.title, interiors, exteriors)

                [interiors_min, interiors_max] = interiors.split("-") if "-" in interiors else [0, interiors]
                [exteriors_min, exteriors_max] = exteriors.split("-") if "-" in exteriors else [0, exteriors]

                

                if interiors_min or exteriors_min:
                    if not interiors_min:
                        interiors_min = interiors_max

                    if not exteriors_min:
                        exteriors_min = exteriors_max

                    
                    tower_plan.total_sqft = f'{int(interiors_min) + int(exteriors_max):,}-{int(interiors_max) + int(exteriors_max):,}'

                else:
                    tower_plan.total_sqft = f'{int(interiors_max) + int(exteriors_max):,}'

                print(tower_plan.title, tower_plan.interiors, tower_plan.exteriors, tower_plan.total_sqft)

                tower_plan.save()

                    
                    
                    
                



                