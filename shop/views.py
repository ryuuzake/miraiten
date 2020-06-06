from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView

from .forms import SearchForm, ShippingForm, CouponForm
from .models import Item, Order, OrderItem


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


class WishlistView(ListView):
    queryset = OrderItem
    template_name = 'shop/wishlist.html'


class SearchView(ListView):
    model = Item
    form_class = SearchForm
    template_name = 'shop/search.html'
    paginate_by = 9

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        context['total_results'] = self.get_queryset().count()
        page = self.request.GET.get("page")
        context['range_result'] = "{}-{}".format(1 * page, self.paginate_by * page)
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
                                           Q(manufacturer__icontains=q))
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
            return None

    def post(self, request, *args, **kwargs):
        pass


class CheckoutView(LoginRequiredMixin, ListView):
    template_name = 'shop/checkout.html'
    shipping_form_class = ShippingForm
    coupon_form_class = CouponForm

    def get_queryset(self):
        try:
            return Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            return None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context.update(**kwargs)
        context['coupon_form'] = self.coupon_form_class(self.request.POST)
        context['shipping_form'] = self.shipping_form_class(self.request.POST)
        return context


class TransactionView(LoginRequiredMixin, ListView):
    template_name = 'shop/transaction.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, ordered=True)


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
