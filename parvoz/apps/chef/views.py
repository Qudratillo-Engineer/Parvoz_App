from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django.db import transaction

from apps.chef.mixins import ChefRequiredMixIns
from apps.orders.models import Order, Notification


class ChefOrderView(LoginRequiredMixin, ChefRequiredMixIns, View):
    
    def get(self, request):
        
        now = timezone.now()
        
        if now.hour < 6:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
        else:
            shift_start = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        orders = (
            Order.objects.select_related(
                "user",
                "table",
                "organization"
            ).prefetch_related(
                "order_items",
                "order_items__food"
            ).filter(
                created_at__gte = shift_start,
                status = Order.OrderStatus.PENDING
            )
        )
        
        data = {
            "orders":orders
        }
        return render(request, "chef/orders.html", context=data)
    


class ChefOrderStatusChangeView(LoginRequiredMixin, ChefRequiredMixIns, View):
    
    def post(self, request):
        
        order_id = request.POST.get("order_id")
        
        if not order_id:
            messages.error(request, "Buyurtma tanlanmadi!")
            return redirect("chef_orders")
        
        try:
            with transaction.atomic():
                
                order = Order.objects.select_for_update().filter(
                    
                    id = order_id,
                    status = Order.OrderStatus.PENDING,
                    organization = request.organization,
                ).first()
                
                if not order:
                    messages.error(request, "Faqat tayyorlanmagan buyurtmani tayyorlash mumkin.")
                    return redirect("chef_orders")
                
                order.status = Order.OrderStatus.READY
                order.save()
                
                
                Notification.objects.create(
                    user=order.user,
                    text=f"#{order.id} - buyurtmangiz tayyor!",
                    type="unviewed"
                )
                
                return redirect("chef_orders")
        except Exception as err:
            
            messages.error(request, "Buyurtmada xato ketdi! ")
            return redirect("chef_orders")



class ChefPollView(LoginRequiredMixin, ChefRequiredMixIns, View):
    def get(self, request):
        latest_order = Order.objects.order_by("-updated_at", "-id").first()
        pending_count = Order.objects.filter(status=Order.OrderStatus.PENDING).count()
        signature = f"{latest_order.updated_at.isoformat() if latest_order else 'none'}:{pending_count}"

        return JsonResponse({
            "signature": signature,
            "pending_count": pending_count,
        })
