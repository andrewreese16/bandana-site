from django.contrib import admin
from .models import Product, Cart, CartItem, Order, ProductImage

# Inline model for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage  # The model to be used inline
    extra = 1  # The number of empty forms to display by default for adding new images

# Register the Product model and attach the ProductImageInline to it
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")
    inlines = [ProductImageInline]  # Attach the inline form to ProductAdmin

# Register other models
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

# Register Cart and CartItem if needed
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
