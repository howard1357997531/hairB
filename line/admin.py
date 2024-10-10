from django.contrib import admin
from .models import *

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'line_user', 'date', 'designer', 'service', 'add_service')

@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'image_url', 'description', 'created_at')

@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'line_user', 'transaction_id', 'transaction_time', 'shipping_state',
        'pickup_method', 'total_price', 'address', 'is_pay', 'created_at')
    
@admin.register(Item)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'name', 'price', 'quantity', 'image_url', 'created_at')

