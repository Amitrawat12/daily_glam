from django.db import models
from django.contrib.auth.models import User

class SavedAdvice(models.Model):
    """Stores the AI-generated advice for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skin_type = models.CharField(max_length=50)
    skin_concerns = models.JSONField()
    age_range = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    skin_tone = models.CharField(max_length=20)
    scent_preference = models.CharField(max_length=20)
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Advice for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
