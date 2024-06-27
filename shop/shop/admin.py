# shop/admin.py

from django.contrib import admin
from .models import Product, Cart, CartItem, Category, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('category',)

    fields = ('name', 'price', 'description', 'category', 'image', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_cost', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'user__username')