from django.contrib import admin
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


admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(Address, AddressAdmin)
