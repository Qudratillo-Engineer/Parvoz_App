from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Food, Order, OrderItem, Table
from apps.waiter.mixins import WaiterRequiredMixIns


class WaiterOrdersView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    def get(self, request):
        
        now = timezone.now()
        
        if now.hour < 6:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
        else:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        orders = (
        Order.objects
        .select_related(
            "user",
            "table",
            "organization"
        )
        .prefetch_related(
            "order_items",
            "order_items__food"
        )
        .filter(
            created_at__gte = shift_start,            user=request.user,
        )
        .order_by("-created_at")
    )
        data = {
            "orders":orders
        }
        return render(request, "waiter/orders.html", context=data)
 
 

class WaiterCreateOrderView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    
    def post(self, request):
        
        table_id = request.POST.get("table_id")
        food_raw = request.POST.get("foods")
        without_table = request.POST.get("without_table") == "1"
        
        if not without_table and not table_id:
            messages.error(request, "Buyurtma uchun stol tanlang yoki stolsiz rejimni yoqing")
            return redirect("waiter_menu")
        
        user = request.user
        
        if not food_raw:
            messages.error(request, "Kamida bitta taom tanlang")
            return redirect("waiter_menu")

        
        try:
            with transaction.atomic():
                if not without_table:
                    table = Table.objects.select_for_update().get(
                        id=table_id,
                        status="free",
                        organization=request.organization,
                    )
                else:
                    table = None
                                    
                order = Order.objects.create(
                    user = user,
                    table = table,
                    organization = request.organization,
                    status = Order.OrderStatus.PENDING
                )
                
                if table:
                    table.status = "occupied"
                    table.save()
                for item in food_raw.split(","):
                    try:
                        food_id, qty = item.split(":")
                    except Exception as err:
                        transaction.set_rollback(True)
                        messages.error(request, "Belgilangan ovqatlarda xato ketdi !")
                        return redirect("waiter_menu")
                    
                    try:
                        food = Food.objects.get(id=food_id, is_active=True)
                    except Food.DoesNotExist:
                        transaction.set_rollback(True)
                        messages.error(request, "Taom topilmadi")
                        return redirect("waiter_menu")
                    
                    try:
                        qty = int(qty)
                    except ValueError:
                        transaction.set_rollback(True)
                        messages.error(request, "Taomlar soni raqam bo'lishi kerak")
                        return redirect("waiter_menu")

                    if qty < 1 or qty > 15:
                        transaction.set_rollback(True)
                        messages.error(request, "Taomlar soni 1 dan 15 gacha bo'lishi kerak")
                        return redirect("waiter_menu")
                    
                    OrderItem.objects.create(
                        order = order,
                        food = food,
                        quantity = qty,
                    )
                    
                return redirect("waiter_orders")
        except Exception as err:
            messages.error(request, f"Xatolik chiqdi iltimos qaytadan urinib ko'ring")
            return redirect("waiter_menu")
                


class WaiterOrderCancelView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    
    def post(self, request):
        
        order_id = request.POST.get("order_id")
        user = request.user
        organization = request.organization
        
        if not order_id:
            messages.error(request, "Buyurtma tanlanmadi!")
            return redirect("waiter_orders")
    
        try:
            order = Order.objects.get(
                id = order_id,
                user = user,
                organization = organization,
            )
            
        except Order.DoesNotExist:
            messages.error(request,"Buyurtma mavjud emas !!")
            return redirect("waiter_orders")
        
        if order.status == Order.OrderStatus.DELIVERED:
            messages.error(request, "Buyurtma allaqachon yetkazilgan!")
            return redirect("waiter_orders")
        
        if order.status == Order.OrderStatus.PAID:
            messages.error(request, "Buyurtma allaqachon yetkazilgan!")
            return redirect("waiter_orders")
        
        if order.status == Order.OrderStatus.CANCELLED:
            messages.error(request, "Buyurtma allaqachon qaytarildi!")
            return redirect("waiter_orders")
        
        order.status = Order.OrderStatus.CANCELLED
        order.save()
        
        return redirect("waiter_orders")



class WaiterOrderChangeStatusView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    
    def post(self, request):
        
        
        order_id = request.POST.get("order_id")
        user = request.user
        organization = request.organization
        
        if not order_id:
            return redirect("waiter_orders")
    
        order = Order.objects.get(
                id = order_id,
                user = user,
                organization = organization,
            )
        if order.status == Order.OrderStatus.DELIVERED:
            messages.error(request, "Buyurtma allaqachon yetkazilgan!")
            return redirect("waiter_orders")
        
        if order.status == Order.OrderStatus.CANCELLED:
            messages.error(request, "Buyurtma allaqachon qaytarildi!")
            return redirect("waiter_orders")
        
        if order.status == Order.OrderStatus.PAID:
            messages.error(request, "Sizda bunday vakolat yoq!")
            return redirect("waiter_orders")
        
        if order.status != Order.OrderStatus.READY:
            messages.error(request, "Buyurtma tayyor emas!")
            return redirect("waiter_orders")
        
        order.status = Order.OrderStatus.DELIVERED
        order.save()
        
        return redirect("waiter_orders")
