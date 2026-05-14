from django.shortcuts import render
from django.views import View


class WaiterDashboardView(View):
    def get(self, request):
        return render(request, "waiter/dashboard.html")
    

class WaiterMenuView(View):
    def get(self, request):
        return render(request, "waiter/menu.html")
    

class WaiterNotificationsView(View):
    def get(self, request):
        return render(request, "waiter/notifications.html")
    

class WaiterOrdersView(View):
    def get(self, request):
        return render(request, "waiter/orders.html")


