from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.accounts.views import RedirectView



urlpatterns = [
    path('admin/', admin.site.urls),
    path("",RedirectView.as_view(), name="redirect"),
    #accounts
    path("auth/",include("apps.accounts.urls")),
    path("waiter/",include("apps.waiter.urls")),
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
