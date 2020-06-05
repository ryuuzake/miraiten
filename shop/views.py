from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from .models import Item, Order, OrderItem


class HomeView(ListView):
    model = Item
    paginate_by = 30
    template_name = 'shop/home.html'


class CartView(LoginRequiredMixin, ListView):
    template_name = 'shop/cart.html'

    def get_queryset(self):
        try:
            return Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        pass


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
