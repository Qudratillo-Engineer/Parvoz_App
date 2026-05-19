from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, ExpressionWrapper, IntegerField

from apps.orders.models import Order, Table, OrderItem
# Create your views here.
from django.views import View


class WaiterDashboardView(LoginRequiredMixin,View):
    def get(self, request):
        
        today_income = OrderItem.objects.filter(
            order__user = request.user,
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("food__price") * F("quantity"),
                    output_field=IntegerField
                )
            )
        )["total"] or 0
        
        orders = Order.objects.prefetch_related(
            "order_items__food"
            ).filter(
            user = request.user
        )
        tables = Table.objects.filter(
            is_active = True
        )
        
        pending_orders = orders.filter(status="pending").order_by("-created_at")
        ready_orders = orders.filter(status="ready").order_by("-created_at")
       
        data = {
            "orders":orders,
            "tables":tables,
            
            "pending_orders":pending_orders,
            "ready_orders":ready_orders,
            "today_income":today_income,
                 
            
        }
        return render(request, "waiter/dashboard.html", context=data)