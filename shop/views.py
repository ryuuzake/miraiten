from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.base import TemplateView

from .forms import SearchForm, ShippingForm
from .models import Item, Order, OrderItem, Wishlist, Address, WishlistItem


class HomeView(TemplateView):
    template_name = 'shop/home.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Item.objects.order_by('-id')[:3]
        context['popular_products'] = Item.objects.order_by('-category__name')[:3]
        return context


class ItemView(DetailView):
    model = Item
    template_name = 'shop/item.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_sellers'] = Item.objects.order_by('-category__name')[:3]
        return context


class WishlistView(LoginRequiredMixin, ListView):
    template_name = 'shop/wishlist.html'

    def get_queryset(self):
        try:
            return Wishlist.objects.get(user=self.request.user)
        except Wishlist.DoesNotExist:
            return Wishlist.objects.none()


@login_required
def toggle_wishlist(request, pk):
    item = get_object_or_404(Item, pk=pk)
    wishlist_item, _ = WishlistItem.objects.get_or_create(item=item, user=request.user)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if wishlist.items.filter(item__pk=item.pk).exists():
        messages.info(request, "This item was deleted to your wishlist", fail_silently=True)
        wishlist.items.remove(wishlist_item)
    else:
        messages.info(request, "This item was added from your wishlist", fail_silently=True)
        wishlist.items.add(wishlist_item)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SearchView(ListView):
    model = Item
    form_class = SearchForm
    template_name = 'shop/search.html'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        page = int(self.request.GET.get("page", 1))
        context['range_result'] = "{} - {}".format(self.paginate_by * page - (self.paginate_by - 1),
                                                   self.paginate_by * page)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            if q:
                queryset = queryset.filter(Q(name__icontains=q) |
                                           Q(series__icontains=q) |
                                           Q(character__icontains=q) |
                                           Q(category__name__icontains=q) |
                                           Q(manufacturer__icontains=q)).order_by('-id')
            if category:
                queryset = queryset.filter(category__in=category)
            return queryset
        return queryset


class CartView(LoginRequiredMixin, ListView):
    template_name = 'shop/cart.html'

    def get_queryset(self):
        try:
            return Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            return Order.objects.none()

    def post(self, request, *args, **kwargs):
        pass


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'shop/checkout.html'
    form_class = ShippingForm
    success_url = reverse_lazy('payment')

    def get_queryset(self):
        try:
            return Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            return None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context.update(**kwargs)
        context['object_list'] = self.get_queryset()
        return context

    def get_initial(self):
        initial = super().get_initial()
        try:
            address = Address.objects.get(user=self.request.user, default=True)
            initial = model_to_dict(address)
        except Address.DoesNotExist:
            initial['user'] = self.request.user
        finally:
            return initial

    def form_valid(self, form):
        order = self.get_queryset()
        if order is not None:
            address = form.create_address()
            order.address = address
            order.ordered = True
            order.save()
        return super(CheckoutView, self).form_valid(form)

    def form_invalid(self, form):
        messages.info(request=self.request, message=str(form.errors), fail_silently=True)
        return super().form_invalid(form)


class TransactionView(LoginRequiredMixin, ListView):
    template_name = 'shop/transaction.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class TransactionDetailView(DetailView):
    model = Order
    template_name = 'shop/transactiondetail.html'


class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/payment.html'


class AccountView(LoginRequiredMixin, ListView):
    template_name = 'shop/account.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated", fail_silently=True)
        else:
            messages.info(request, "This item was added to your cart", fail_silently=True)
            order.items.add(order_item)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    except Order.DoesNotExist:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart", fail_silently=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if order.items.filter(item__pk=item.pk).exists():
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This was added to your cart", fail_silently=True)
        else:
            messages.warning(request, "This item was not in your cart", fail_silently=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    except Order.DoesNotExist:
        messages.warning(request, "You don't have active order", fail_silently=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_single_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if order.items.filter(item__pk=item.pk).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.warning(request, "This item quantity was updated", fail_silently=True)
        else:
            messages.warning(request, "This item was not in your cart", fail_silently=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    except Order.DoesNotExist:
        messages.warning(request, "You don't have active order", fail_silently=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
