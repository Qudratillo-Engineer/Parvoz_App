from django.core.exceptions import PermissionDenied

class AdminRequiredMixIns:
    def dispatch(self, request, *args, **kwargs):
        
        user = request.user
        
        if not user.is_authenticated:
            raise PermissionDenied("Siz tizimga kirmagansiz !")
        
        if user.is_active == False:
            raise PermissionDenied("You are in_active user !")
        
        membership = user.memberships.filter(role = "admin").first()
        
        if not membership:
            raise PermissionDenied("Sizni tizimdagi bu rolingiz topilmadi !")
        
        return super().dispatch(request, *args, **kwargs)
        
        
        
        