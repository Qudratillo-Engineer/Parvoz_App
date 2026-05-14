from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db import transaction

from apps.orders.models import Food, Order, OrderItem, Table


class WaiterOrdersView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, "waiter/orders.html")
    
class WaiterCreateOrderView(LoginRequiredMixin,View):
    def post(self, request):
        
        table_id = request.POST.get("table_id")
        food_raw = request.POST.get("foods")
        
        user = request.user
        membership = user.memberships.all().first()
        
        if food_raw is None:
            return redirect("waiter_menu")
        if membership is None:
            raise PermissionError(
                "You need membership from our ORG to do this action !!!"
                )
        organization = membership.organization
        print(organization, food_raw)
        try:
            with transaction.atomic():
                
                table = get_object_or_404(Table, id=table_id)
                
                total = 0
                foods_items = []
                
                for item in food_raw.split(","):
                    food_id, qty = item.split(":")
                    food = get_object_or_404(Food, id=food_id)
                    total += food.price * int(qty)
                    qty = int(qty)
                    foods_items.append({
                        "food":food,
                        "qty":qty
                    })
                    
                
                order = Order.objects.create(
                    user = user,
                    table = table,
                    organization = organization,
                    total = total
                )
                
                
                for food in foods_items:
                    OrderItem.objects.create(
                        order = order,
                        food = food["food"],
                        quantity = food["qty"]
                    )
                
                return redirect("waiter_orders")
        except Exception as err:
            print(err)
            print("Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail !Error Fail ! ")
            return redirect("dashboard")