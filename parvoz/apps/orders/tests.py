from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Organization, OrganizationMembership
from apps.orders.models import Food, Order, OrderItem, Table


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "cache-for-ratelimiting": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
)
class BackendProtectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.org = Organization.objects.create(name="Org A", type="cafe")
        self.other_org = Organization.objects.create(name="Org B", type="cafe")
        self.waiter = self.user("waiter", "waiter", self.org)
        self.chef = self.user("chef", "chef", self.org)
        self.cashier = self.user("cashier", "accounter", self.org)
        self.admin = self.user("admin", "admin", self.org)
        self.other_waiter = self.user("other", "waiter", self.other_org)
        self.food = Food.objects.create(name="Soup", type="main", price=10, description="Hot")
        self.table = Table.objects.create(number=1, type="in", organization=self.org)
        self.other_table = Table.objects.create(number=2, type="in", organization=self.other_org)

    def user(self, username, role, organization):
        user = get_user_model().objects.create_user(username=username, password="pass12345")
        OrganizationMembership.objects.create(user=user, role=role, organization=organization)
        return user

    def login(self, user):
        self.client.force_login(user)

    def order(self, user=None, organization=None, table=None, status=Order.OrderStatus.PENDING):
        order = Order.objects.create(
            user=user or self.waiter,
            organization=organization or self.org,
            table=table,
            status=status,
        )
        OrderItem.objects.create(order=order, food=self.food, quantity=1)
        return order

    # Checks anonymous user cannot access waiter dashboard
    def test_waiter_dashboard_requires_login(self):
        self.assertEqual(self.client.get(reverse("waiter_dashboard")).status_code, 302)

    # Checks cashier cannot access chef orders
    def test_cashier_cannot_access_chef_orders(self):
        self.login(self.cashier)
        self.assertEqual(self.client.get(reverse("chef_orders")).url, "/auth/access-denied/")

    # Checks chef cannot access cashier dashboard
    def test_chef_cannot_access_cashier_dashboard(self):
        self.login(self.chef)
        self.assertEqual(self.client.get(reverse("cashier_dashboard")).url, "/auth/access-denied/")

    # Checks waiter cannot access admin dashboard
    def test_waiter_cannot_access_admin_dashboard(self):
        self.login(self.waiter)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).url, "/auth/access-denied/")

    # Checks logout ends authenticated session
    def test_logout_clears_session(self):
        self.login(self.waiter)
        self.client.get(reverse("logout"))
        self.assertFalse("_auth_user_id" in self.client.session)

    # Checks repeated bad logins are rate limited
    def test_login_rate_limit_blocks_repeated_posts(self):
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "bad", "password": "bad"})
        self.assertEqual(self.client.post(reverse("login"), {"username": "bad", "password": "bad"}).status_code, 403)

    # Checks waiter can create order for own organization table
    def test_waiter_can_create_order(self):
        self.login(self.waiter)
        self.client.post(reverse("create_order"), {"table_id": self.table.id, "foods": f"{self.food.id}:2"})
        self.assertEqual(Order.objects.filter(user=self.waiter, table=self.table).count(), 1)

    # Checks waiter cannot create order for another organization table
    def test_waiter_cannot_create_order_for_other_org_table(self):
        self.login(self.waiter)
        self.client.post(reverse("create_order"), {"table_id": self.other_table.id, "foods": f"{self.food.id}:2"})
        self.assertFalse(Order.objects.filter(table=self.other_table).exists())

    # Checks empty order payload is rejected
    def test_create_order_rejects_empty_foods(self):
        self.login(self.waiter)
        self.client.post(reverse("create_order"), {"table_id": self.table.id})
        self.assertFalse(Order.objects.exists())

    # Checks invalid quantity is rejected
    def test_create_order_rejects_invalid_quantity(self):
        self.login(self.waiter)
        self.client.post(reverse("create_order"), {"table_id": self.table.id, "foods": f"{self.food.id}:0"})
        self.assertFalse(Order.objects.exists())

    # Checks invalid food ID is rejected
    def test_create_order_rejects_invalid_food_id(self):
        self.login(self.waiter)
        self.client.post(reverse("create_order"), {"table_id": self.table.id, "foods": "999:1"})
        self.assertFalse(Order.objects.exists())

    # Checks waiter can cancel own pending order
    def test_waiter_can_cancel_pending_order(self):
        order = self.order()
        self.login(self.waiter)
        self.client.post(reverse("cancel_order"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.CANCELLED)

    # Checks waiter cannot cancel another organization order
    def test_waiter_cannot_cancel_other_org_order(self):
        order = self.order(user=self.other_waiter, organization=self.other_org, table=self.other_table)
        self.login(self.waiter)
        self.client.post(reverse("cancel_order"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PENDING)

    # Checks paid order cannot be cancelled
    def test_paid_order_cannot_be_cancelled(self):
        order = self.order(status=Order.OrderStatus.PAID)
        self.login(self.waiter)
        self.client.post(reverse("cancel_order"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PAID)

    # Checks chef can mark pending order ready
    def test_chef_can_mark_pending_order_ready(self):
        order = self.order()
        self.login(self.chef)
        self.client.post(reverse("chef_status_ready"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.READY)

    # Checks chef cannot mark cancelled order ready
    def test_chef_cannot_mark_cancelled_order_ready(self):
        order = self.order(status=Order.OrderStatus.CANCELLED)
        self.login(self.chef)
        self.client.post(reverse("chef_status_ready"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.CANCELLED)

    # Checks chef cannot ready another organization order
    def test_chef_cannot_ready_other_org_order(self):
        order = self.order(user=self.other_waiter, organization=self.other_org, table=self.other_table)
        self.login(self.chef)
        self.client.post(reverse("chef_status_ready"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PENDING)

    # Checks waiter can deliver ready order
    def test_waiter_can_deliver_ready_order(self):
        order = self.order(status=Order.OrderStatus.READY)
        self.login(self.waiter)
        self.client.post(reverse("change_order_status"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.DELIVERED)

    # Checks waiter cannot deliver cancelled order
    def test_waiter_cannot_deliver_cancelled_order(self):
        order = self.order(status=Order.OrderStatus.CANCELLED)
        self.login(self.waiter)
        self.client.post(reverse("change_order_status"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.CANCELLED)

    # Checks cashier can mark delivered order paid
    def test_cashier_can_mark_delivered_order_paid(self):
        order = self.order(table=self.table, status=Order.OrderStatus.DELIVERED)
        self.login(self.cashier)
        self.client.post(reverse("cashier_order_paid"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PAID)

    # Checks paid order frees table
    def test_paid_order_frees_table(self):
        self.table.status = Table.TableStatus.OCCUPIED
        self.table.save()
        order = self.order(table=self.table, status=Order.OrderStatus.DELIVERED)
        self.login(self.cashier)
        self.client.post(reverse("cashier_order_paid"), {"order_id": order.id})
        self.table.refresh_from_db()
        self.assertEqual(self.table.status, Table.TableStatus.FREE)

    # Checks cashier cannot pay pending order
    def test_cashier_cannot_pay_pending_order(self):
        order = self.order(status=Order.OrderStatus.PENDING)
        self.login(self.cashier)
        self.client.post(reverse("cashier_order_paid"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PENDING)

    # Checks cashier cannot pay another organization order
    def test_cashier_cannot_pay_other_org_order(self):
        order = self.order(user=self.other_waiter, organization=self.other_org, table=self.other_table, status=Order.OrderStatus.DELIVERED)
        self.login(self.cashier)
        self.client.post(reverse("cashier_order_paid"), {"order_id": order.id})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.DELIVERED)

    # Checks CSRF blocks waiter order creation POST
    def test_create_order_requires_csrf_token(self):
        self.csrf_client.force_login(self.waiter)
        response = self.csrf_client.post(reverse("create_order"), {"table_id": self.table.id, "foods": f"{self.food.id}:1"})
        self.assertEqual(response.status_code, 403)
