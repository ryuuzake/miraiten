from django.urls import path
from .views import (
    HomeView,
    CartView,
    add_to_cart,
    delete_from_cart,
    remove_single_from_cart,
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('cart/', CartView.as_view(), name="cart"),
    path('cart/add/<int:pk>/', add_to_cart, name="add-to-cart"),
    path('cart/remove/<int:pk>/', remove_single_from_cart, name="remove-single-from-cart"),
    path('cart/delete/<int:pk>/', delete_from_cart, name="delete-from-cart"),
]
