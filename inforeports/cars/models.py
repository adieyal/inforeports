from django.db import models

class CarAd(models.Model):
    title = models.CharField(max_length=100)
    date_listed = models.DateField()
    price = models.FloatField()
    address = models.TextField(blank=True)
    seller_type = models.CharField(max_length=20)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    body_type = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=4)
    mileage = models.IntegerField()
    transmission = models.CharField(max_length=20, blank=True)
    drive_train = models.CharField(max_length=40, blank=True)
    air_conditioning = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    province = models.CharField(max_length=40, blank=True)
    area = models.CharField(max_length=40, blank=True)
    suburb = models.CharField(max_length=40, blank=True)
    hash = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (self.title)

class CarModel(models.Model):
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s - %s' % (self.make, self.model)
