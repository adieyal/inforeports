from django.db import models

class CarAd(models.Model):
    title = models.CharField(max_length=100)
    date_listed = models.DateField()
    price = models.FloatField()
    address = models.TextField()
    seller_type = models.CharField(max_length=20)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    body_type = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    mileage = models.IntegerField()
    transmission = models.CharField(max_length=20)
    drive_train = models.CharField(max_length=20)
    air_conditioning = models.CharField(max_length=20)
    description = models.TextField()
    province = models.CharField(max_length=20)
    area = models.CharField(max_length=20)
    suburb = models.CharField(max_length=20)
    hash = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % (self.title)
