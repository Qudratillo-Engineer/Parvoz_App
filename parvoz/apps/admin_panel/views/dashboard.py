from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.admin_panel.mixins import AdminRequiredMixIns

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixIns, View):
    
    def get(self, request):
        
        
        
        return render(request,"admin_panel/dashboard.html")