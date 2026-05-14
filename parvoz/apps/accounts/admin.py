from django.contrib import admin
from apps.accounts.models import (
    Organization,OrganizationMembership,
    
)
# Register your models here.

admin.site.register([
    Organization,OrganizationMembership,
  ])