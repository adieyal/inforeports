import csv

from django.contrib import admin
from django.http import HttpResponse
import models

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        queryset = modeladmin.model.objects.all()
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset
        
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
        
        writer = csv.writer(response)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode('utf-8') for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv

class CarAdAdmin(admin.ModelAdmin):
    list_display = ("province", "make", "model", "year", "mileage", "price")
    list_filter = ("make", "model", "year", "province")
    date_hierarchy = "date_listed"
    actions = [export_as_csv_action("Export model as CSV file", header=True)]

class CarModelAdmin(admin.ModelAdmin):
    list_display = ("make", "model")
    list_filter = ("make", "model")

admin.site.register(models.CarAd, CarAdAdmin)
admin.site.register(models.CarModel, CarModelAdmin)
