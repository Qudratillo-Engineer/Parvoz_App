from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.orders.models import Table


class WaiterTablesView(LoginRequiredMixin,View):
    
    def get(self, request):
        
        tables = Table.objects.all()
        
        data = {
            "tables": tables
        }
        return render(request, "waiter/tables.html", context=data)

    def post(self, request):
        pass