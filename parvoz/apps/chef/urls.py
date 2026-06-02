from django.urls import path

from apps.chef.views import ChefOrderView, ChefOrderStatusChangeView, ChefPollView

urlpatterns = [
    path("orders/", ChefOrderView.as_view(), name="chef_orders"),
    path("orders/change_status/", ChefOrderStatusChangeView.as_view(), name="chef_status_ready"),
    path("poll/", ChefPollView.as_view(), name="chef_poll"),
]
