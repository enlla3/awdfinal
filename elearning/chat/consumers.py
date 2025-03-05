import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from courses.models import Course
from django.contrib.auth import get_user_model

from .models import ChatMessage


class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the course ID
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        # Create a unique room group name using the course ID
        self.room_group_name = f"course_chat_{self.course_id}"

        # Add the channel to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the channel from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the JSON data
        data = json.loads(text_data)
        message = data.get("message", "")
        user = self.scope.get("user")
        # Get the username
        username = user.username if user and user.is_authenticated else "Anonymous"

        # Save the message to the database
        await self.save_message(user, message)

        # Broadcast the message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        # Retrieve the message and username from the
        message = event["message"]
        username = event["username"]
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
        }))

    @sync_to_async
    def save_message(self, user, message):
        from chat.models import ChatMessage
        from courses.models import Course
        course = Course.objects.get(id=self.course_id)
        # If the user is not authenticated, do not save the message
        if not user.is_authenticated:
            return
        # Get the concrete user instance
        User = get_user_model()
        actual_user = User.objects.get(pk=user.pk)
        # Create and save the chat message
        ChatMessage.objects.create(course=course, sender=actual_user, message=message)
