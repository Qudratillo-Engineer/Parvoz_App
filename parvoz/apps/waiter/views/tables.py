from django.views import View
from django.shortcuts import render

from apps.orders.models import Table


class WaiterTablesView(View):
    def get(self, request):
        
        tables = Table.objects.all()
        
        data = {
            "tables": tables
        }
        
        return render(request, "waiter/tables.html")
    
