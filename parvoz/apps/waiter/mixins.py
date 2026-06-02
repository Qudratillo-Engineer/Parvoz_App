from django.shortcuts import redirect

class WaiterRequiredMixIns:
    def dispatch(self, request, *args, **kwargs):
        
        user = request.user
        
        if not user.is_authenticated:
            return redirect("/auth/access-denied/")
        
        
        membership = user.memberships.filter(role = "waiter").first()
        if not membership:
            return redirect("/auth/access-denied/")
        request.membership = membership
        request.organization = membership.organization
        
        return super().dispatch(request, *args, **kwargs)
        
        
        
        