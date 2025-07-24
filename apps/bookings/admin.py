from django.contrib import admin
from .models import Service, Order


# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "place")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("service", "time_start", "time_end", "status", "full_name_client", "total_price")
    list_filter = ("status", "service")
    search_fields = ("client_name", "client_contact")