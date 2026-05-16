from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.orders.models import Order, Table
# Create your views here.
from django.views import View


class WaiterDashboardView(LoginRequiredMixin,View):
    def get(self, request):
        today_income = 0
        orders = Order.objects.prefetch_related(
            "order_items__food"
                ).filter(
                    user=request.user
                        ).order_by("-created_at")
        tables = Table.objects.all()
        
        for order in orders:
            today_income += order.total
        
        
        active_orders = orders.filter(status="pending").order_by("-created_at")
        ready_orders = orders.filter(status="ready").order_by("-created_at")
        
        data = {
            "orders":orders,
            "tables":tables,
            
            "active_orders":active_orders,
            "ready_orders":ready_orders,
            "today_income":today_income,
                 
            
        }
        return render(request, "waiter/dashboard.html", context=data)