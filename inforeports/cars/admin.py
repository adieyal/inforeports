from django.contrib import admin
import models

class CarAdAdmin(admin.ModelAdmin):
    list_display = ("province", "make", "model", "year", "mileage", "price")
    list_filter = ("make", "model", "year", "province")

admin.site.register(models.CarAd, CarAdAdmin)
