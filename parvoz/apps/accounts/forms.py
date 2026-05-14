from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):

    username = forms.CharField(required=True)
    password = forms.CharField(required=True)

    
    
class RegisterForm(forms.Form):

    username = forms.CharField(required=True)
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)
    phone = forms.CharField(required=True, max_length=20)
    role = forms.CharField(max_length=25,required=True)
    organization = forms.CharField(max_length=25,required=True)


    def clean(self):

        attrs = super().clean()

        username = attrs.get('username')
        password = attrs.get('password1')
        password2 = attrs.get('password2')
        phone = attrs.get('phone')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number already exists")

        if password2 != password:
            print(password, password2)
            raise forms.ValidationError("Passwords do not match")

        return attrs
    def save(self, cleaned_data):
        return User.objects.create_user(**cleaned_data)

