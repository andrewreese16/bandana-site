from django import forms
from .models import Order

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone_number', 'shipping_address']
