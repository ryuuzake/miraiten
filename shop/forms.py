from django import forms

from .models import Category, Address, Coupon


class SearchForm(forms.Form):
    q = forms.CharField(required=False)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code']
