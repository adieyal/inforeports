from django.core.management.base import BaseCommand, CommandError
from scrape import scrape_cars
from cars.models import CarAd, CarModel, CarAttributes
import re

def create_regexp(keywords):
    return re.compile("\\b(?:%s)\\b" % "|".join(keywords))


re_bluetooth = create_regexp(["bluetooth"])
re_dvd = create_regexp(["dvd"])
re_cd = create_regexp(["cd", "r/cd"])
re_abs = create_regexp(["abs"])
re_ps = create_regexp(["power steering", "ps", "p/s", "powersteering"])
re_ew = create_regexp(["electric windows", "ew", "e/w", "e/w/m"])
re_diesel = create_regexp(["diesel"])
re_petrol = create_regexp(["petrol"])
re_electric_mirrors = create_regexp(["electric mirrors", "e/m", "e/w/m"])
re_radio = create_regexp(["radio", "r/cd"])
re_aircon = create_regexp(["aircon", "air conditioning", "airconditioning", "ac", "a/c", "air con"])
re_leather = create_regexp(["leather"])
re_fsh = create_regexp(["fsh", "full service history", "service history"])
re_serviceplan = create_regexp(["service plan"])
re_maintenanceplan = create_regexp(["maintenance plan"])
re_mp3 = create_regexp(["mp3"])
re_mags = create_regexp(["mags", "alloy"])
re_sunroof = create_regexp(["sunroof", "sun roof", "s/roof"])
re_lady = create_regexp(["lady driver", "lady owner", "lady owned", "lady"])

class Command(BaseCommand):
    help = "Tries to mine ad attributes from the description"

    def has_attr(self, description, regexp):
        if regexp.search(description.lower()):
            return True
        return False

    def extract_attributes(self, ad):
        description = ad.description.lower() + ad.title.lower()
        return {
            "has_bluetooth" : self.has_attr(description, re_bluetooth),
            "has_dvd" : self.has_attr(description, re_dvd),
            "has_cd" : self.has_attr(description, re_cd),
            "has_abs" : self.has_attr(description, re_abs),
            "has_ps" : self.has_attr(description, re_ps),
            "has_ew" : self.has_attr(description, re_ew),
            "has_diesel" : self.has_attr(description, re_diesel),
            "has_petrol" : self.has_attr(description, re_petrol),
            "has_electric_mirrors" : self.has_attr(description, re_electric_mirrors),
            "has_radio" : self.has_attr(description, re_radio),
            "has_aircon" : self.has_attr(description, re_aircon),
            "has_leather" : self.has_attr(description, re_leather),
            "has_fsh" : self.has_attr(description, re_fsh),
            "has_serviceplan" : self.has_attr(description, re_serviceplan),
            "has_maintenanceplan" : self.has_attr(description, re_maintenanceplan),
            "has_mp3" : self.has_attr(description, re_mp3),
            "has_mags" : self.has_attr(description, re_mags),
            "has_sunroof" : self.has_attr(description, re_sunroof),
            "has_lady" : self.has_attr(description, re_lady),
        }

    def sm_vw_polo(self, description):
        is_playa = self.has_attr(description, create_regexp(["playa"]))
        is_comfortline = self.has_attr(description, create_regexp(["comfortline", "comfort line"]))
        is_trendline = self.has_attr(description, create_regexp(["trendline", "trend line"]))
        is_tdi_19 = self.has_attr(description, create_regexp(["1.9tdi", "1.9 tdi", "tdi 1.9"]))
        is_tdi_14 = self.has_attr(description, create_regexp(["1.4tdi", "1.4 tdi", "tdi 1.4"]))
        is_tdi_12 = self.has_attr(description, create_regexp(["1.2tdi", "1.2 tdi", "tdi 1.2"]))
        is_vivo = self.has_attr(description, create_regexp(["vivo"]))
        is_classic = self.has_attr(description, create_regexp(["classic", "clasic"]))
        is_16 = self.has_attr(description, create_regexp(["1.6i", "1.6"]))
        is_16 = self.has_attr(description, create_regexp(["1.6i", "1.6"]))
        is_16s = self.has_attr(description, create_regexp(["1.6s"]))
        is_14 = self.has_attr(description, create_regexp(["1.4i", "1.4"]))
        is_18 = self.has_attr(description, create_regexp(["1.8i", "1.8"]))
        is_2l = self.has_attr(description, create_regexp(["2l", "2ltr", "2.0"]))
        is_gti = self.has_attr(description, create_regexp(["gti"]))
        is_bluemotion = self.has_attr(description, create_regexp(["bluemotion", "blue motion"]))
        if not any([is_playa, is_comfortline, is_trendline, is_tdi_19, is_vivo, is_classic, is_16, is_14, is_gti, is_bluemotion, is_18]):
            print description.encode("utf8")
        return ""

    def determine_submodel(self, ad):
        description = ad.title + " " + ad.description
        make_model = ad.make + " " + ad.model
        submodel_map = {
            "Volkswagen Polo Vivo" : self.sm_vw_polo
        }

        foo = submodel_map.get(make_model, lambda x : "")
        foo(description)
        
        

    def handle(self, *args, **kwargs):
        for ad in CarAd.objects.all():
            self.determine_submodel(ad)
            #self.extract_attributes(ad)
