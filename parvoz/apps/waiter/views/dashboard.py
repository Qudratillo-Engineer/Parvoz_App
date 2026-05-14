from django.shortcuts import render

# Create your views here.
from django.views import View


class WaiterDashboardView(View):
    def get(self, request):
        return render(request, "waiter/dashboard.html")