from django.urls import path
from apps.waiter.views.tables import WaiterTablesView
from apps.waiter.views.dashboard import WaiterDashboardView
from apps.waiter.views.orders import WaiterOrdersView
from apps.waiter.views.menu import WaiterMenuView
from apps.waiter.views.notifications import WaiterNotificationsView

urlpatterns = [
    
    path("dashboard/", WaiterDashboardView.as_view(), name="waiter_dashboard"),
    path("orders/", WaiterOrdersView.as_view(), name="waiter_orders"),
    path("menu/", WaiterMenuView.as_view(), name="waiter_menu"),
    path("notifications/", WaiterNotificationsView.as_view(), name="waiter_notifications"),
    path("tables/", WaiterTablesView.as_view(), name="waiter_tables"),
    
]
