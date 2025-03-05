from django.urls import path

from . import consumers

# Define the URL patterns
websocket_urlpatterns = [
    # Map the WebSocket URL 
    path('ws/course_chat/<int:course_id>/', consumers.CourseChatConsumer.as_asgi()),
]
