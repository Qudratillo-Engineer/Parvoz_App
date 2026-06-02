from django.urls import path

from apps.admin_panel.views.dashboard import AdminDashboardView, AdminPollView

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("poll/", AdminPollView.as_view(), name="admin_poll"),
]
