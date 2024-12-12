# store/context_processors.py
from .models import Cart, CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # Get the total number of items in the cart
            return {"cart_item_count": sum(item.quantity for item in CartItem.objects.filter(cart=cart))}
    return {"cart_item_count": 0}
