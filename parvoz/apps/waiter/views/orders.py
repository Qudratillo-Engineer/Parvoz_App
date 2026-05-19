from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db import transaction

from apps.orders.models import Food, Order, OrderItem, Table


class WaiterOrdersView(LoginRequiredMixin,View):
    def get(self, request):
        
        
        orders = Order.objects.prefetch_related(
            "order_items__food"
                ).filter(
                    user=request.user
                        ).order_by("-created_at")
        
        data = {
            "orders":orders
        }
        return render(request, "waiter/orders.html", context=data)
 
 

class WaiterCreateOrderView(LoginRequiredMixin,View):
    
    def post(self, request):
        
        table_id = request.POST.get("table_id")
        food_raw = request.POST.get("foods")
        without_table = request.POST.get("without_table") == "1"
        if not without_table and not table_id:
            messages.error(request, "Buyurtma uchun stol tanlang yoki stolsiz rejimni yoqing")
            return redirect("waiter_menu")
        table = None if without_table else get_object_or_404(Table, id=table_id)
        user = request.user
        membership = user.memberships.all().first()
        
        if table and table.status == "occupied":
            messages.error(request, "Belgilangan stol allaqachon band!")
            return redirect("waiter_menu")
        if not food_raw:
            messages.error(request, "Kamida bitta taom tanlang")
            return redirect("waiter_menu")
        if membership is None:
            messages.error(request, "Tashkilotga a'zo emassiz")
            return redirect("dashboard")
            
        organization = membership.organization
     
        
        try:
            with transaction.atomic():
                
                order = Order.objects.create(
                    user = user,
                    table = table,
                    organization = organization,
                    status = "pending"
                )
                if table:
                    table.status = "occupied"
                    table.save()
                for item in food_raw.split(","):
                    food_id, qty = item.split(":")
                    food = get_object_or_404(Food, id=food_id)
                    qty = int(qty)
                    OrderItem.objects.create(
                        order = order,
                        food = food,
                        quantity = qty,
                    )
                    
                return redirect("waiter_orders")
        except Exception as err:
            messages.error(request, f"Xatolik: {str(err)}")
            return redirect("waiter_menu")
                


class WaiterOrderCancelView(LoginRequiredMixin,View):
    
    def post(self, request):
        
        order_id = request.POST.get("order_id")
        
        if not order_id:
            messages.error(request, "Buyurtma tanlanmadi!")
            return redirect("waiter_orders")
    
        try:
            order = Order.objects.get(id = order_id)
        except Order.DoesNotExist():
            messages.error(request,"Buyurtma mavjud emas !!")
            return redirect("waiter_orders")
        
        if order.status == "delivered":
            messages.error(request, "Buyurtma allaqachon yetkazilgan!")
            return redirect("waiter_orders")
        
        if order.status == "cancelled":
            messages.error(request, "Buyurtma allaqachon qaytarildi!")
            return redirect("waiter_orders")
        order.delete()
        return redirect("waiter_orders")


class WaiterOrderChangeStatusView(LoginRequiredMixin,View):
    
    def post(self, request):
        
        order_id = request.POST.get("order_id")
        
        if not order_id:
            return redirect("waiter_orders")
    
        order = get_object_or_404(Order, id=order_id)
        if not order:
            messages.error(request, "Buyutmada xato kelib chiqdi!")
            return redirect("waiter_orders")
        
        if order.status == "delivered":
            messages.error(request, "Buyurtma allaqachon yetkazilgan!")
            return redirect("waiter_orders")
        
        if order.status == "cancelled":
            messages.error(request, "Buyurtma allaqachon qaytarildi!")
            return redirect("waiter_orders")
        
        if order.status == "paid":
            messages.error(request, "Sizda bunday vakolat yoq!")
            return redirect("waiter_orders")
        
        if order.status != "ready":
            messages.error(request, "Buyurtma tayyor emas!")
            return redirect("waiter_orders")
        
        order.status = "delivered"
        order.save()
        
        return redirect("waiter_orders")
