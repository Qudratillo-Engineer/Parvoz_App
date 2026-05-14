from django.urls import path
from apps.waiter.views.tables import WaiterTablesView
from apps.waiter.views.dashboard import WaiterDashboardView
from apps.waiter.views.orders import WaiterOrdersView, WaiterCreateOrderView
from apps.waiter.views.menu import WaiterMenuView, WaiterMenuWithTableView
from apps.waiter.views.notifications import WaiterNotificationsView

urlpatterns = [
    
    path("dashboard/", WaiterDashboardView.as_view(), name="waiter_dashboard"),
    
    path("orders/", WaiterOrdersView.as_view(), name="waiter_orders"),
    path("orders/create/", WaiterCreateOrderView.as_view(), name="create_order"),
    
    path("menu/", WaiterMenuView.as_view(), name="waiter_menu"),
    path("menu/table/<int:table_id>", WaiterMenuWithTableView.as_view(), name="waiter_menu_table"),
    
    path("notifications/", WaiterNotificationsView.as_view(), name="waiter_notifications"),
    
    path("tables/", WaiterTablesView.as_view(), name="waiter_tables"),
    
]
