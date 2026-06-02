from django.shortcuts import render 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.orders.models import Notification, Order
from apps.waiter.mixins import WaiterRequiredMixIns

class WaiterNotificationsView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user,
            is_active=True,
        ).order_by("-created_at")
        
        return render(
            request,
            "waiter/notifications.html",
            {"notifications": notifications},
        )


class WaiterNotificationsCheckView(LoginRequiredMixin,WaiterRequiredMixIns, View):
    def get(self, request):
        # Сначала читаем — принудительно evaluate
        notifications = list(Notification.objects.filter(
            user=request.user,
            type="unviewed"
        ).values("id", "text", "created_at"))
        
        # Потом помечаем как viewed
        Notification.objects.filter(
            user=request.user,
            type="unviewed"
        ).update(type="viewed")
        
        return JsonResponse({
            "count": len(notifications),
            "notifications": notifications
        })


class WaiterPollView(LoginRequiredMixin,WaiterRequiredMixIns, View):
    def get(self, request):
        latest_order = Order.objects.filter(user=request.user).order_by("-updated_at", "-id").first()
        unread_count = Notification.objects.filter(user=request.user, type="unviewed").count()
        signature = f"{latest_order.updated_at.isoformat() if latest_order else 'none'}:{unread_count}"

        return JsonResponse({
            "signature": signature,
            "unread_count": unread_count,
        })
