from django.urls import path
from . import views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy


urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("cart/", views.cart_view, name="cart_view"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("cancel/", views.cancel, name="cancel"),
    path("remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path(
        "signup/",
        CreateView.as_view(
            template_name="registration/signup.html",
            form_class=UserCreationForm,
            success_url=reverse_lazy("login"),
        ),
        name="signup",
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
