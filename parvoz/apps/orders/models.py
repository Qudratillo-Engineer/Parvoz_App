from django.db import models
from apps.accounts.models import User
from apps.accounts.models import Organization
# Create your models here.

class BaseModel(models.Model):
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        abstract = True  

    

class Table(BaseModel):
    
    class TableType(models.TextChoices):
        INDOOR = 'in', 'INDOOR'
        OUTDOOR = 'out', 'OUTDOOR'
    
    class TableStatus(models.TextChoices):
        FREE = 'free', 'FREE'
        OCCUPIED = 'occupied', 'OCCUPIED'
        
    number = models.IntegerField()
    
    type = models.CharField(
        choices=TableType.choices,
        max_length=3)
    
    status = models.CharField(
        choices=TableStatus.choices,
        default=TableStatus.FREE,
        max_length=10,
        db_index=True)
    
    def __str__(self):
        return f"Table {self.number} - {self.type}"
    
    

class Food(BaseModel):
    
    class FoodType(models.TextChoices):
        MAIN = "main", "MAIN"
        DRINK = "drink", "DRINK"
        DESSERT = "dessert", "DESSERT" 
    
    name = models.CharField(max_length=100)
    type = models.CharField(
        choices=FoodType.choices,
        max_length=10,
        db_index=True
    )
    price = models.PositiveIntegerField()
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    
    
class Order(BaseModel):
    
    class OrderStatus(models.TextChoices):
        PENDING = "pending", 'Pending'
        READY = "ready", 'Ready'
        DELIVERED = "delivered", 'Delivered'
        CANCELLED = "cancelled", 'Cancelled'
        PAID = "paid", "Paid"
        
    
    
    organization = models.ForeignKey(
        Organization,
        related_name="orders",
        on_delete=models.CASCADE
    )
    
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.CASCADE
    )

    table = models.ForeignKey(
        Table,
        related_name="orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        max_length=14,
        db_index=True
    )
    
    
    @property
    def total(self):
        return sum(
            item.food.price * item.quantity 
            for item in self.order_items.all()
        )
    
    def __str__(self):
        return F"{self.id}# {self.status}"

    class Meta:
        indexes = [
            models.Index(fields=["table", "user", "status"]),
            models.Index(fields=["user","table"])
        ]
    
class OrderItem(BaseModel):
    
    order = models.ForeignKey(
        Order,
        related_name="order_items",
        on_delete=models.CASCADE
    )
    food = models.ForeignKey(
        Food,
        related_name="order_items",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.food.name

class Notification(BaseModel):
    
    class NotificationType(models.TextChoices):
        VIEWED = "viewed", "VIEWED"
        UNVIEWED = "unviewed", "UNVIEWED"

    user = models.ForeignKey(
        User,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    
    text = models.TextField()
    type = models.CharField(
        choices=NotificationType.choices,
        max_length=10,
        db_index=True
    )
    
    def __str__(self):
        return self.text
    
    
    

    
        
        
        
        
        
    