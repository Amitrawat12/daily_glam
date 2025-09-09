from django.db import models
from django.contrib.auth.models import User

class Kit(models.Model):
    """Represents a user's saved beauty kit."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kit for {self.user.username}"

class KitItem(models.Model):
    """Represents a single product item within a user's kit."""
    kit = models.ForeignKey(Kit, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=100) # A unique ID for the product
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField()
    site = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return self.name
