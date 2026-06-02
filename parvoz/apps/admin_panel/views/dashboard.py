from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import F, Sum, ExpressionWrapper, IntegerField

from apps.admin_panel.mixins import AdminRequiredMixIns
from apps.orders.models import Order, OrderItem

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixIns, View):
    
    def get(self, request):
        total_orders = Order.objects.count()
        today_income = OrderItem.objects.filter(
            order__status=Order.OrderStatus.PAID,
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("food__price") * F("quantity"),
                    output_field=IntegerField()
                )
            )
        )["total"] or 0

        return render(request, "admin_panel/dashboard.html", {
            "total_orders": total_orders,
            "today_income": today_income,
        })


class AdminPollView(LoginRequiredMixin, AdminRequiredMixIns, View):
    def get(self, request):
        latest_order = Order.objects.order_by("-updated_at", "-id").first()
        signature = f"{latest_order.updated_at.isoformat() if latest_order else 'none'}:{Order.objects.count()}"

        return JsonResponse({
            "signature": signature,
        })
