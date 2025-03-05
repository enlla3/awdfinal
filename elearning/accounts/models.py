from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    # Role field
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    # Real name field, optional
    real_name = models.CharField(max_length=100, blank=True)
    # Photo field for profile picture, optional
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.username

class StatusUpdate(models.Model):
    # Foreign key to the custom user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='status_updates')
    # Content of the status update
    content = models.TextField()
    # Timestamp for the status update
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status by {self.user.username} at {self.created_at}"
