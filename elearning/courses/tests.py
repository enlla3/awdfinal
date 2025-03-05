from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Course, Feedback, Material, Notification

User = get_user_model()

class CoursesTests(TestCase):
    def setUp(self):
        # Create teacher and student users
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
        # Create a course with teacher as owner
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            teacher=self.teacher
        )

    def test_course_list_view_for_student(self):
        # Test that student can view course list
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('courses:course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)

    def test_teacher_can_add_course(self):
        # Test that teacher can add a new course
        self.client.login(username='teacher1', password='pass123')
        data = {
            'title': 'New Course',
            'description': 'New Course Description'
        }
        response = self.client.post(reverse('courses:add_course'), data)
        new_course = Course.objects.get(title='New Course')
        self.assertRedirects(response, reverse('courses:course_detail', args=[new_course.id]))

    def test_student_cannot_add_course(self):
        # Test that student cannot add a new course
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('courses:add_course'))
        self.assertRedirects(response, reverse('courses:course_list'))

    def test_student_enroll_in_course(self):
        # Test that student can enroll in a course
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('courses:enroll_course', args=[self.course.id]))
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.id]))
        self.assertIn(self.student, self.course.enrolled_students.all())
        # Verify that teacher gets a notification about the new enrollment
        notif = Notification.objects.filter(user=self.teacher, message__contains=self.student.username)
        self.assertTrue(notif.exists())

    def test_student_cannot_view_materials_if_not_enrolled(self):
        # Test that student cannot view materials if not enrolled
        material_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        self.client.login(username='teacher1', password='pass123')
        response = self.client.post(
            reverse('courses:upload_material', args=[self.course.id]),
            {'file': material_file}
        )
        self.assertEqual(self.course.materials.count(), 1)
        # Un-enrolled student viewing course detail should not see material link
        self.client.logout()
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('courses:course_detail', args=[self.course.id]))
        self.assertNotContains(response, "Download Material")

    def test_student_feedback(self):
        # Test that student can add feedback
        self.client.login(username='student1', password='pass123')
        response = self.client.post(
            reverse('courses:add_feedback', args=[self.course.id]),
            {'comment': 'Great course!'}
        )
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.id]))
        self.assertEqual(self.course.feedbacks.count(), 1)

    def test_teacher_remove_student(self):
        # Test that teacher can remove a student from the course
        self.course.enrolled_students.add(self.student)
        self.client.login(username='teacher1', password='pass123')
        response = self.client.get(reverse('courses:remove_student', args=[self.course.id, self.student.id]))
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.id]))
        self.assertNotIn(self.student, self.course.enrolled_students.all())
        notif = Notification.objects.filter(user=self.student, message__icontains="removed")
        self.assertTrue(notif.exists())

    def test_teacher_block_and_unblock_student(self):
        # Test that teacher can block and unblock a student
        self.course.enrolled_students.add(self.student)
        self.client.login(username='teacher1', password='pass123')
        # Block student
        response = self.client.get(reverse('courses:block_student', args=[self.course.id, self.student.id]))
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.id]))
        self.assertIn(self.student, self.course.blocked_students.all())
        notif = Notification.objects.filter(user=self.student, message__icontains="banned")
        self.assertTrue(notif.exists())
        # Unblock student
        response = self.client.get(reverse('courses:unblock_student', args=[self.course.id, self.student.id]))
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.id]))
        self.assertNotIn(self.student, self.course.blocked_students.all())

    def test_notifications_view(self):
        # Test that student can view notifications
        Notification.objects.create(user=self.student, message="Test notification")
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('courses:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test notification")
