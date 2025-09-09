from django.db import models
from django.contrib.auth.models import User

class SavedComparison(models.Model):
    """Represents a user's saved product comparison."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255) # e.g., "My Foundation Comparison"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ComparisonItem(models.Model):
    """Represents a single product within a saved comparison."""
    comparison = models.ForeignKey(SavedComparison, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField()
    site = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return self.name
