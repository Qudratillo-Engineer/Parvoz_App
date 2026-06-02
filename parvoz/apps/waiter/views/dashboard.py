from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, ExpressionWrapper, IntegerField
from django.views import View
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, Table, OrderItem
from apps.waiter.mixins import WaiterRequiredMixIns
# Create your views here.


class WaiterDashboardView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    def get(self, request):
        
        now = timezone.now()
        
        if now.hour < 6:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
        else:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        today_income = OrderItem.objects.filter(
            order__user = request.user,
            order__created_at__gte = shift_start,
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("food__price") * F("quantity"),
                    output_field=IntegerField()
                )
            )
        )["total"] or 0
        
        orders = Order.objects.prefetch_related(
            "order_items__food"
            ).filter(
            user = request.user,
            created_at__gte = shift_start,
        )
        tables = Table.objects.filter(
            is_active = True
        )
        
        pending_orders = orders.filter(status=Order.OrderStatus.PENDING).order_by("-created_at")
        ready_orders = orders.filter(status=Order.OrderStatus.READY).order_by("-created_at")
       
        data = {
            "orders":orders,
            "tables":tables,
            
            "pending_orders":pending_orders,
            "ready_orders":ready_orders,
            "active_orders_count":pending_orders.count(),
            "ready_orders_count":ready_orders.count(),
            "today_income":today_income,
                 
            
        }
        return render(request, "waiter/dashboard.html", context=data)
