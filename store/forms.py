from django import forms
from .models import Order


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone_number", "shipping_address"]

    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Full Name"}
        ),
    )
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        ),
    )
    shipping_address = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Shipping Address (Street, City, State, Zip)",
                "rows": 4,
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Order.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
