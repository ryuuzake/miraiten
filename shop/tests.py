from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from shop.models import Item, Category, OrderItem, Order
from shop.views import add_to_cart, remove_single_from_cart, delete_from_cart


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
        self.assertEqual(str(order), f"{self.user.username}")

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
