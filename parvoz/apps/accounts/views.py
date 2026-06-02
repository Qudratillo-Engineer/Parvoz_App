from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from apps.accounts.models import User
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import transaction

from .forms import LoginForm, RegisterForm
from .models import OrganizationMembership, Organization, Activities
# Create your views here.

class RedirectView(View):
    def get(self, request):
        return redirect("login")


def get_authenticated_redirect(user):
    membership = user.memberships.first()
    if membership is None:
        return "access_denied"

    role_redirects = {
        "waiter": "waiter_dashboard",
        "admin": "admin_dashboard",
        "chef": "chef_orders",
        "accounter": "cashier_dashboard",
    }
    return role_redirects.get(membership.role, "login")


class AccessDeniedView(View):
    def get(self, request):
        return render(request, "auth/access_denied.html", {
            "next_url": request.GET.get("next", ""),
        })


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="dispatch")
class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(get_authenticated_redirect(request.user))
        
        return render(request, "auth/login_standalone.html")
    
    
    def post(self, request):
            if request.user.is_authenticated:
                return redirect(get_authenticated_redirect(request.user))
        
            form = LoginForm(data = request.POST)

            if not form.is_valid():
                return render(request, "auth/login_standalone.html", context={"form":form})

            username = form.cleaned_data.get('username', None)
            password = form.cleaned_data.get('password', None)

          
            user = authenticate(request, username=username, password=password)
           
            if user is not None:
                login(request, user)
                membership = OrganizationMembership.objects.filter(user=user).first()
                if membership is not None:
                    
                    Activities.objects.create(
                        organization=membership.organization,
                        user=user,
                        action=f"{membership.organization}'s user {user.username} logged in !"
                    )
                    return redirect(get_authenticated_redirect(user))
                
                return render(request, "auth/login_standalone.html", context={
                    "error_log":"Sizni tizimda rolingiz mavjud emas. Iltimos ADMIN ga murojat qiling !!",
                    "form":form})
                
            return render(request, "auth/login_standalone.html", context={
                "error_log":"Sizni Login va Parolingiz notug'ri !! | Siz tizimda mavjud emassiz !!",
                "form":form})

@method_decorator(ratelimit(key="ip", rate="3/m", method="POST", block=True), name="dispatch")
class RegisterView(View):
    
    def get_context_data(self, **kwargs):
        context = dict(**kwargs)
        context["organizations"] = Organization.objects.filter(is_active=True)
        return context
    

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(get_authenticated_redirect(request.user))

        return render(request, "auth/register_standalone.html",
                      self.get_context_data())
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect(get_authenticated_redirect(request.user))
        
        form = RegisterForm(data = request.POST)
        
        
        if not form.is_valid():
            return render(request, "auth/register_standalone.html",
                          self.get_context_data(form = form))
       
        try:
            with transaction.atomic():
        
                user = User(
                    username = form.cleaned_data.get('username'),
                    phone = form.cleaned_data.get('phone'),
                )
                user.set_password(str(form.cleaned_data.get('password1')))
                user.save()
                # Get organization
                organization = Organization.objects.get(id=form.cleaned_data.get('organization'))

                OrganizationMembership.objects.create(
                    user = user,
                    organization = organization,
                    role = form.cleaned_data.get('role'),
                )
                
                
                Activities.objects.create(
                        user = user,
                        action = f"User {user.username} registered, please give attention!",
                        organization = organization,
                )
                return redirect("login")
        except Organization.DoesNotExist as err:
            return render(request, "auth/register_standalone.html", self.get_context_data(form = form, error_org = "Tashkilot topilmadi"))
        
@method_decorator(ratelimit(key="ip", rate="3/m", method="POST", block=True), name="dispatch")
class Logout(View):
    
    def get(self, request):
        
        logout(request)
        return redirect("login")

    def post(self, request):
        logout(request)
        return redirect("login")
