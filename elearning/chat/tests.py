import json

from channels.testing import WebsocketCommunicator
from courses.models import Course
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from elearning.asgi import application

User = get_user_model()

class ChatTests(TestCase):
    def setUp(self):
        # Set up test users and course
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123',
            role='teacher',
            email='teacher1@example.com',
            real_name='Teacher One'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            email='student1@example.com',
            real_name='Student One'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            teacher=self.teacher
        )
        self.course.enrolled_students.add(self.student)
        self.client = Client()

    def test_course_chat_room_view_for_enrolled_student(self):
        # Test chat room view for an enrolled student
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)

    def test_course_chat_room_view_for_non_enrolled_student(self):
        # Test chat room view for a non-enrolled student
        other_student = User.objects.create_user(
            username='student2',
            password='pass123',
            role='student',
            email='student2@example.com',
            real_name='Student Two'
        )
        self.client.login(username='student2', password='pass123')
        response = self.client.get(reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertContains(response, "You are not enrolled in this course.")

    async def test_course_chat_consumer(self):
        # Test the chat consumer using
        communicator = WebsocketCommunicator(application, f"/ws/course_chat/{self.course.id}/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        # Send a test message
        test_message = "Hello, course chat!"
        await communicator.send_json_to({"message": test_message})
        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], test_message)
        await communicator.disconnect()

    def test_chat_history_loaded_in_template(self):
        # Test if chat history is loaded in the template
        from chat.models import ChatMessage
        ChatMessage.objects.create(course=self.course, sender=self.student, message="Historical message")
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertContains(response, "Historical message")
