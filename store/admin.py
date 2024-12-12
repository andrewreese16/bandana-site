from django.contrib import admin
from .models import Product, Cart, CartItem, Order

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "total_price",
        "date",
    )
    list_filter = ("date",)
    search_fields = (
        "user__username",
        "product__name",
    )
    ordering = ("-date",)
    readonly_fields = (
        "id",
        "user",
        "product",
        "quantity",
        "total_price",
        "date",
    )
