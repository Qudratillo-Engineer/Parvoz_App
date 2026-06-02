from django.contrib import admin
from apps.accounts.models import (
    Organization,OrganizationMembership,User,Activities
    
)
# Register your models here.

admin.site.register([
    Organization,OrganizationMembership,User,Activities
  ])