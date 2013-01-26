from django.core.management.base import BaseCommand, CommandError
from scrape import scrape_cars
from cars.models import CarAd, CarModel
import re

class Command(BaseCommand):
    help = "Tries to correct missing car models"

    def handle(self, *args, **kwargs):
        for ad in CarAd.objects.filter(model="Other"):
            make = ad.make
            carmodels = CarModel.objects.filter(make=make)
            description = ad.description.lower() + ad.title.lower()
            selected_models = []
            for carmodel in carmodels:
                if len(carmodel.model) < 3: continue
                regex = re.compile("\\b%s\\b" % carmodel.model.lower())
                if regex.search(description):
                    selected_models.append(carmodel.model)
            if len(selected_models) == 1:
                ad.model = selected_models[0]
                ad.save()
            print len(selected_models)
