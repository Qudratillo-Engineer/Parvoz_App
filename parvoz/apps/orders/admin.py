from django.contrib import admin

from apps.orders.models import Order, Food, Table, Notification

# Register your models here.
admin.site.register([Order, Food, Table, Notification])