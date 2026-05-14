from django.shortcuts import render

# Create your views here.
from django.views import View


class WaiterOrdersView(View):
    def get(self, request):
        return render(request, "waiter/orders.html")