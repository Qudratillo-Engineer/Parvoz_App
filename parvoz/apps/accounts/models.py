from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class OrganizationChoices(models.TextChoices):
    
    CAFE = "cafe", "Cafe"
    RESTORAN = "restoran", "Restoran"



class RoleChoice(models.TextChoices):
    
    WAITER = "waiter", "Waiter"
    CHEF = "chef", "Chef"
    ACCOUNTER = "accounter", "Accounter"
    ADMIN = "admin", "ADMIN"



class BaseModel(models.Model):
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  



class Organization(BaseModel):
    
    name = models.CharField(max_length=100)
    type = models.CharField(
        choices=OrganizationChoices.choices,
        max_length=15
    )
    
    def __str__(self):
        return self.name
 
    

class OrganizationMembership(BaseModel):
    
    organization = models.ForeignKey(
        Organization,
        related_name="memberships",
        on_delete=models.CASCADE
    )
    role = models.CharField(
        choices=RoleChoice.choices,
        max_length=25,
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        related_name="memberships",
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return f"{self.user.username} --> {self.organization.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=["organization", "user"]),
            models.Index(fields=["user", "organization"]),
            models.Index(fields=["user", "role"]),   
        ]
        

class Activities(BaseModel):
    
    organization = models.ForeignKey(
        Organization,
        related_name="activities",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="activities",
        on_delete=models.CASCADE
    )
    action = models.TextField()
