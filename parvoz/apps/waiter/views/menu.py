from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.waiter.mixins import WaiterRequiredMixIns
from apps.orders.models import Food
# Create your views here.



class WaiterMenuView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    def get(self, request):
        
        menu_items = Food.objects.filter(is_active = True)
        
        data = {
            "menu_items":menu_items
        }
        return render(request, "waiter/menu.html", context=data)
    


class WaiterMenuWithTableView(LoginRequiredMixin,WaiterRequiredMixIns,View):
    
    def get(self, request, table_id):
        
        menu_items = Food.objects.all()
        
        data = {
            "table_id":table_id,
            "menu_items":menu_items
        }
        
        return render(request, "waiter/menu.html", context=data)