from django import forms

from .models import Category, Address, Coupon


class SearchForm(forms.Form):
    q = forms.CharField(required=False)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)


class ShippingForm(forms.ModelForm):

    def create_address(self):
        return Address.objects.get_or_create(self.cleaned_data)

    class Meta:
        model = Address
        fields = '__all__'


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code']
