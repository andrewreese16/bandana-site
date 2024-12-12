from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order
from django.conf import settings
import stripe
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ShippingForm
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def remove_from_cart(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            messages.success(
                request, f"{cart_item.product.name} has been removed from your cart."
            )
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in cart.")
    return redirect("cart_view")


def product_list(request):
    cart_item_count = 0

    # Check if the user is authenticated before accessing cart
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_item_count = (
            sum(item.quantity for item in cart.cartitem_set.all()) if cart else 0
        )

    products = Product.objects.all()
    if not products.exists():
        messages.error(request, "No products available at the moment.")

    return render(
        request,
        "store/product_list.html",
        {
            "cart_item_count": cart_item_count,
            "products": products,
        },
    )


def cart_view(request):
    cart_items = []
    total = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart) if cart else []
        total = sum(item.product.price * item.quantity for item in cart_items)

    return render(
        request, "store/cart_view.html", {"cart_items": cart_items, "total": total}
    )


def add_to_cart(request, product_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # Store the intended product_id in the session
        request.session["intended_product_id"] = product_id
        # Add a message to explain why they're being redirected
        messages.warning(
            request, "Please log in or create an account to add items to your cart."
        )
        # Redirect to login page
        return redirect("login")  # Replace 'login' with your actual login URL name

    # Rest of the existing add_to_cart logic remains the same
    product = get_object_or_404(Product, id=product_id)

    # Get the user's cart, or create one if it doesn't exist
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If the item is already in the cart, increment the quantity by 1
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"One more {product.name} added to your cart.")
        else:
            messages.warning(
                request,
                f"Sorry, only {product.stock} of {product.name} available in stock.",
            )
    else:
        # If the product is not in the cart, create a new cart item with quantity 1
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f"{product.name} added to your cart.")

    return redirect("cart_view")


def login_view(request):
    # Your existing login authentication logic here

    # After successful login, check if there was an intended product to add to cart
    if "intended_product_id" in request.session:
        product_id = request.session.pop("intended_product_id")
        return redirect("add_to_cart", product_id=product_id)

    # Otherwise, proceed with normal login redirect
    return redirect("product_list")


@login_required
def checkout(request):
    try:
        # Get the user's cart and items
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart_view")

        # Create an order only when the user clicks 'Continue to Payment'
        if request.method == "POST":
            # Create order entries for each cart item
            orders = []
            for item in cart_items:
                order = Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.product.price * item.quantity,
                    name=request.POST["name"],  # Assuming form input fields
                    email=request.POST["email"],
                    phone_number=request.POST["phone_number"],
                    shipping_address=request.POST["shipping_address"],
                )
                orders.append(order)

            # Now that the orders are created, send the session data to Stripe
            return redirect("payment_page")

        else:
            form = ShippingForm()

        # Render the checkout page
        return render(
            request,
            "store/checkout.html",
            {"total": total, "cart_items": cart_items, "form": form},
        )

    except Cart.DoesNotExist:
        messages.error(request, "No cart found. Please add items to your cart.")
        return redirect("cart_view")


@login_required
@csrf_exempt
def create_checkout_session(request):
    try:
        # Parse incoming request data
        data = json.loads(request.body)
        order_id = data.get("order_id")  # Optional, but can be useful

        # Fetch the cart items for the current user (do not delete the cart here!)
        cart_items = CartItem.objects.filter(cart__user=request.user)

        # Ensure that there are items in the cart before proceeding
        if not cart_items:
            return JsonResponse({"error": "No items in the cart"}, status=400)

        # Initialize line items list
        line_items = []

        # Populate the line items from the cart items
        for item in cart_items:
            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",  # Use your preferred currency
                        "product_data": {
                            "name": item.product.name,  # Product name
                        },
                        "unit_amount": int(item.product.price * 100),  # Price in cents
                    },
                    "quantity": item.quantity,  # Quantity from the cart item
                }
            )

        # Debugging line items to verify the data
        print(line_items)

        # Create the Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri("/success/"),
            cancel_url=request.build_absolute_uri("/cancel/"),
        )

        # Return the session ID to the frontend
        return JsonResponse({"sessionId": session.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "order_history.html", {"orders": orders})


def cancel(request):
    return render(request, "cancel.html")


def payment_page(request):
    # Render the payment page
    return render(request, "store/payment_page.html")
