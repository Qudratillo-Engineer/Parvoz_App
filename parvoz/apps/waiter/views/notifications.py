from django.shortcuts import render 
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.views import View

class WaiterNotificationsView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, "waiter/notifications.html")