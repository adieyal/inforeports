from django.core.management.base import BaseCommand, CommandError
from scrape import scrape_cars
from cars.models import CarAd


class Command(BaseCommand):
    help = "Scrapes car data from Gumtree"

    def process_entry(self, vals):
        if vals:
            del vals["last_edited"]
            if CarAd.objects.filter(hash=vals["hash"]).count() == 0:
                CarAd.objects.create(**vals)

    def handle(self, *args, **kwargs):
        scrape_cars.get_entries(callback=self.process_entry)
