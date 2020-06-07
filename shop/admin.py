import csv
import io

from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.db import transaction
from django.urls import path

from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'address',
        'payment',
        'coupon'
    ]
    list_display_links = [
        'user',
        'address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received']
    search_fields = [
        'user__username',
        'ref_code'
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street',
        'province',
        'city',
        'postal_code',
        'phone_number',
        'default'
    ]
    list_filter = ['default', 'province', 'city']
    search_fields = ['user', 'address', 'phone_number', 'postal_code']


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class CsvImportMixins(admin.ModelAdmin):
    change_list_template = "shop/item_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"].read().decode("utf-8")
            self.process_csv(csv.DictReader(io.StringIO(csv_file)))
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        return render(request, "admin/csv_form.html", {"form": CsvImportForm()})

    @transaction.atomic
    def process_csv(self, reader):
        pass


class ItemAdmin(CsvImportMixins):

    @transaction.atomic
    def process_csv(self, reader):
        for row in reader:
            category, _ = Category.objects.get_or_create(name=row['category'])
            Item.objects.get_or_create(name=row['name'], category=category, price=row['price'],
                                       series=row['series'], character=row['character'],
                                       manufacturer=row['manufacturer'], description=row['description'],
                                       image=row['image'])


class ProvinceAdmin(CsvImportMixins):

    @transaction.atomic
    def process_csv(self, reader):
        for row in reader:
            Province.objects.get_or_create(pk=int(row['province_id']), name=row['name'])


class CityAdmin(CsvImportMixins):

    @transaction.atomic
    def process_csv(self, reader):
        for row in reader:
            province, _ = Province.objects.get_or_create(pk=int(row['province_id']))
            City.objects.get_or_create(pk=int(row['district_id']), name=row['name'], province=province)


admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
