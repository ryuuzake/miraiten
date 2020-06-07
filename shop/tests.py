from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from shop.models import Item, Category, OrderItem, Order, Wishlist
from shop.views import (
    add_to_cart,
    remove_single_from_cart,
    delete_from_cart,
    add_to_wishlist,
    remove_from_wishlist,
    SearchView
)


class CategoryTest(TestCase):

    @staticmethod
    def create_category(name="test"):
        return Category.objects.create(name=name)

    def test_category_creation(self):
        category = self.create_category()
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(str(category), category.name)


class ItemTest(TestCase):

    def setUp(self) -> None:
        self.category = CategoryTest.create_category()

    @staticmethod
    def create_item(name="only a test", category=Category(1), price=190_000.0,
                    discount_price=150_000.0, description="yes, this is only a test",
                    slug="only-a-test", image="http://example.com"):
        return Item.objects.create(name=name, category=category, price=price,
                                   discount_price=discount_price, description=description,
                                   slug=slug, image=image)

    def test_item_creation(self):
        item = self.create_item(category=self.category)
        self.assertTrue(isinstance(item, Item))
        self.assertEqual(str(item), item.name)


class OrderItemTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='jacob', email='jacob@example.com', password='top_secret')
        self.category = CategoryTest.create_category()
        self.item = ItemTest.create_item(category=self.category)

    @staticmethod
    def create_order_item(user, item, quantity=1):
        return OrderItem.objects.create(user=user, item=item, quantity=quantity)

    def test_order_item_creation(self):
        order_item = OrderItemTest.create_order_item(user=self.user, item=self.item)
        self.assertTrue(isinstance(order_item, OrderItem))
        self.assertEqual(str(order_item), f"{order_item.quantity} of {order_item.item.name}")

    def test_order_item_get_total_item_price(self):
        order_item = OrderItemTest.create_order_item(user=self.user, item=self.item, quantity=2)
        self.assertEqual(order_item.get_total_item_price(), 380_000.0)


class OrderTest(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@example.com', password='top_secret')
        self.category = CategoryTest.create_category()
        self.item = ItemTest.create_item(category=self.category)
        self.order_item = OrderItemTest.create_order_item(user=self.user, item=self.item)

    @staticmethod
    def create_order(user, order_item):
        order = Order.objects.create(user=user)
        order.items.add(order_item)
        return order

    def test_order_creation(self):
        order = OrderTest.create_order(user=self.user, order_item=self.order_item)
        self.assertTrue(isinstance(order, Order))
        self.assertEqual(str(order), f"Order of {self.user.username}")

    def test_order_add_to_cart(self):
        order = OrderTest.create_order(user=self.user, order_item=self.order_item)

        request = self.factory.get(f'/cart/add/{self.item.pk}/')
        request.user = self.user
        response = add_to_cart(request, self.item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.items.get(item__pk=self.item.pk).quantity, 2)

    def test_order_remove_single_from_cart(self):
        item = ItemTest.create_item(name="testing 2", category=self.category)
        order_item = OrderItemTest.create_order_item(user=self.user, item=item, quantity=2)
        order = OrderTest.create_order(user=self.user, order_item=order_item)

        request = self.factory.get(f'/cart/remove/{item.pk}/')
        request.user = self.user
        response = remove_single_from_cart(request, item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.items.get(item__pk=item.pk).quantity, 1)

    def test_order_delete_from_cart(self):
        order = OrderTest.create_order(user=self.user, order_item=self.order_item)

        request = self.factory.get(f'/cart/delete/{self.item.pk}/')
        request.user = self.user
        response = delete_from_cart(request, self.item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(order.items.exists())


class WishlistTest(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@example.com', password='top_secret')
        self.category = CategoryTest.create_category()
        self.item = ItemTest.create_item(category=self.category)
        self.order_item = OrderItemTest.create_order_item(user=self.user, item=self.item)

    @staticmethod
    def create_wishlist(user, order_item):
        wishlist = Wishlist.objects.create(user=user)
        wishlist.items.add(order_item)
        return wishlist

    def test_wishlist_creation(self):
        wishlist = WishlistTest.create_wishlist(user=self.user, order_item=self.order_item)
        self.assertTrue(isinstance(wishlist, Wishlist))
        self.assertEqual(str(wishlist), f"Wishlist of {self.user.username}")

    def test_wishlist_add_to_wishlist(self):
        wishlist = WishlistTest.create_wishlist(user=self.user, order_item=self.order_item)

        request = self.factory.get(f'/wishlist/add/{self.item.pk}/')
        request.user = self.user
        response = add_to_wishlist(request, self.item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(wishlist.items.get(item__pk=self.item.pk).quantity, 2)

    def test_wishlist_remove_from_wishlist(self):
        wishlist = WishlistTest.create_wishlist(user=self.user, order_item=self.order_item)

        request = self.factory.get(f'/wishlist/remove/{self.item.pk}/')
        request.user = self.user
        response = remove_from_wishlist(request, self.item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(wishlist.items.exists())


class SearchViewTest(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@example.com', password='top_secret')
        self.category = CategoryTest.create_category()
        self.item = ItemTest.create_item(category=self.category)
        self.order_item = OrderItemTest.create_order_item(user=self.user, item=self.item)

    def test_search_q(self):
        request = self.factory.get(f'search?q=Tanjiro')
        response = SearchView.as_view()(request)
        self.assertEqual(response.status_code, 200)
