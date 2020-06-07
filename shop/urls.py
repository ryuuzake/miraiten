from django.urls import path
from .views import (
    HomeView,
    ItemView,
    SearchView,
    WishlistView,
    CartView,
    add_to_cart,
    delete_from_cart,
    remove_single_from_cart,
    CheckoutView,
    TransactionView,
    TransactionDetailView,
    PaymentView,
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('item/<int:pk>/<str:slug>/', ItemView.as_view(), name="item"),
    path('search', SearchView.as_view(), name="search"),
    path('wishlist/', WishlistView.as_view(), name="wishlist"),
    path('cart/', CartView.as_view(), name="cart"),
    path('cart/add/<int:pk>/', add_to_cart, name="add-to-cart"),
    path('cart/remove/<int:pk>/', remove_single_from_cart, name="remove-single-from-cart"),
    path('cart/delete/<int:pk>/', delete_from_cart, name="delete-from-cart"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('transaction/', TransactionView.as_view(), name="transaction"),
    path('transaction/<int:pk>/', TransactionDetailView.as_view(), name="transaction-detail"),
    path('payment/', PaymentView.as_view(), name="payment"),
]
