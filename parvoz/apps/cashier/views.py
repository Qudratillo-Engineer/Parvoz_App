from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, ExpressionWrapper, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.db import transaction

from apps.cashier.mixins import CashierRequiredMixIns
from apps.orders.models import Order, OrderItem


def get_shift_start():
    now = timezone.now()
    if now.hour < 6:
        return now.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
    return now.replace(hour=6, minute=0, second=0, microsecond=0)


def get_shift_start_for(dt):
    local_dt = timezone.localtime(dt)
    if local_dt.hour < 6:
        return local_dt.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
    return local_dt.replace(hour=6, minute=0, second=0, microsecond=0)


def get_shift_orders(request):
    
    organization = request.organization
    
    return Order.objects.prefetch_related(
        "order_items__food"
    ).filter(organization=organization).select_related("table", "user", "organization")


def get_paid_income(queryset):
    return OrderItem.objects.filter(
        order__in=queryset,
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("food__price") * F("quantity"),
                output_field=IntegerField()
            )
        )
    )["total"] or 0


class CashierDashboardView(LoginRequiredMixin, CashierRequiredMixIns, View):
    def get(self, request):
        shift_start = get_shift_start()
        orders = get_shift_orders(request).filter(
            created_at__gte=shift_start,
        ).order_by("-created_at")

        payable_orders = orders.filter(status=Order.OrderStatus.DELIVERED)
        paid_orders = orders.filter(status=Order.OrderStatus.PAID)
        today_income = get_paid_income(paid_orders)

        return render(request, "cashier/dashboard.html", {
            "orders": orders,
            "payable_orders": payable_orders,
            "paid_orders": paid_orders,
            "payable_count": payable_orders.count(),
            "paid_count": paid_orders.count(),
            "today_income": today_income,
        })


class CashierPaymentsView(LoginRequiredMixin, CashierRequiredMixIns, View):
    def get(self, request):
        shift_start = get_shift_start()
        payable_orders = get_shift_orders(request).filter(
            status=Order.OrderStatus.DELIVERED,
            created_at__gte=shift_start,
        ).order_by("created_at")

        return render(request, "cashier/payments.html", {
            "payable_orders": payable_orders,
            "payable_count": payable_orders.count(),
        })


class CashierReportView(LoginRequiredMixin, CashierRequiredMixIns, View):
    def get(self, request):
        paid_orders = list(get_shift_orders(request).filter(
            status=Order.OrderStatus.PAID,
        ).order_by("-updated_at"))
        shift_map = {}

        for order in paid_orders:
            shift_start = get_shift_start_for(order.updated_at)
            key = shift_start.isoformat()
            if key not in shift_map:
                shift_map[key] = {
                    "shift_start": shift_start,
                    "shift_end": shift_start + timedelta(days=1),
                    "orders_count": 0,
                    "income": 0,
                    "orders": [],
                }

            shift_map[key]["orders_count"] += 1
            shift_map[key]["income"] += order.total
            shift_map[key]["orders"].append(order)

        shifts = sorted(
            shift_map.values(),
            key=lambda shift: shift["shift_start"],
            reverse=True,
        )

        return render(request, "cashier/report.html", {
            "shifts": shifts,
            "total_income": sum(shift["income"] for shift in shifts),
            "total_orders": sum(shift["orders_count"] for shift in shifts),
        })


class CashierOrderPaidView(LoginRequiredMixin, CashierRequiredMixIns, View):
    def post(self, request):
        
        order_id = request.POST.get("order_id")
        
        if not order_id:
            messages.error(request, "Buyurtma tanlanmadi!")
            return redirect("cashier_payments")

        try:
            with transaction.atomic(): 
                
                order = Order.objects.select_for_update().filter(
                    id = order_id,
                    status = Order.OrderStatus.DELIVERED,
                    organization = request.organization,
                ).first()
                
                if not order:
                    messages.error(request, "Faqat yetkazilgan buyurtmani to'lash mumkin.")
                    return redirect("cashier_payments")

                order.status = Order.OrderStatus.PAID
                order.save()

                if order.table:
                    order.table.status = "free"
                    order.table.save()
                    
                messages.success(request, f"#{order.id} buyurtma to'landi.")
                return redirect("cashier_payments")
            
        except Exception as err: 
            
            messages.error(request, "Buyutrmada xato ketdi !!! ")
            return redirect('cashier_payments')
            

class CashierPollView(LoginRequiredMixin, CashierRequiredMixIns, View):
    def get(self, request):
        
        latest_order = Order.objects.filter(organization=request.organization).order_by("-updated_at", "-id").first()
        delivered_count = Order.objects.filter(organization=request.organization,status=Order.OrderStatus.DELIVERED).count()
        signature = f"{latest_order.updated_at.isoformat() if latest_order else 'none'}:{delivered_count}"

        return JsonResponse({
            "signature": signature,
            "delivered_count": delivered_count,
        })
