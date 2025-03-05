from courses.models import Course
from django.conf import settings
from django.db import models

class ChatMessage(models.Model):
    # Foreign key to the Course model
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_messages')
    # Foreign key to the user model
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Text field to store the message content
    message = models.TextField()
    # DateTime field to store the time of the message
    timestamp = models.DateTimeField(auto_now_add=True)

    # String representation of ChatMessage 
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
