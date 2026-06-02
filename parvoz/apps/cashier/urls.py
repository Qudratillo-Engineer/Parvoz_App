from django.urls import path

from apps.cashier.views import (
    CashierDashboardView,
    CashierOrderPaidView,
    CashierPaymentsView,
    CashierPollView,
    CashierReportView,
)


urlpatterns = [
    path("dashboard/", CashierDashboardView.as_view(), name="cashier_dashboard"),
    path("payments/", CashierPaymentsView.as_view(), name="cashier_payments"),
    path("report/", CashierReportView.as_view(), name="cashier_report"),
    path("orders/paid/", CashierOrderPaidView.as_view(), name="cashier_order_paid"),
    path("poll/", CashierPollView.as_view(), name="cashier_poll"),
]
