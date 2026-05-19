from django.urls import path

from apps.admin_panel.views.dashboard import AdminDashboardView

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin_dashboard")
]
