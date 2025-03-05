from accounts.models import StatusUpdate
from courses.models import Course
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        # Create a teacher and a student.
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="pass123",
            role="teacher",
            email="teacher1@example.com",
            real_name="Teacher One"
        )
        self.student = User.objects.create_user(
            username="student1",
            password="pass123",
            role="student",
            email="student1@example.com",
            real_name="Student One"
        )
        # Create courses
        self.teacher_course = Course.objects.create(
            title="Teacher Course",
            description="Course created by teacher",
            teacher=self.teacher
        )
        self.student_course = Course.objects.create(
            title="Student Course",
            description="Course where student is enrolled",
            teacher=self.teacher
        )
        # Enroll the student in a course.
        self.student_course.enrolled_students.add(self.student)

        # Create status updates
        self.teacher_status = StatusUpdate.objects.create(
            user=self.teacher,
            content="Teacher status update"
        )
        self.student_status = StatusUpdate.objects.create(
            user=self.student,
            content="Student status update"
        )

    def test_register_view_get(self):
        # Test GET request to the register view.
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post(self):
        # Test POST request to the register view.
        data = {
            'username': 'newstudent',
            'real_name': 'New Student',
            'email': 'newstudent@example.com',
            'role': 'student',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertRedirects(response, reverse('accounts:home'))
        new_user = User.objects.get(username='newstudent')
        self.assertEqual(new_user.real_name, 'New Student')

    def test_login_and_logout(self):
        # Test login and logout functionality.
        login_response = self.client.post(
            reverse('accounts:login'),
            {'username': 'student1', 'password': 'pass123'}
        )
        self.assertRedirects(login_response, reverse('accounts:home'))
        logout_response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(logout_response, reverse('accounts:login'))

    def test_home_view_status_update(self):
        # Test posting a status update on the home view.
        self.client.login(username='student1', password='pass123')
        response = self.client.post(reverse('accounts:home'), {'content': 'Hello, status!'})
        self.assertRedirects(response, reverse('accounts:home'))
        response = self.client.get(reverse('accounts:home'))
        self.assertContains(response, "Hello, status!")

    def test_teacher_search_view(self):
        # Test the search view for teachers.
        self.client.login(username='teacher1', password='pass123')
        response = self.client.get(reverse('accounts:search_users') + '?q=student')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')

    def test_student_cannot_access_search_view(self):
        # Test that students cannot access the search view.
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('accounts:search_users'))
        self.assertRedirects(response, reverse('accounts:home'))

    def test_teacher_public_profile(self):
        # Test the public profile view for teachers.
        url = reverse("accounts:public_profile", args=[self.teacher.username])
        self.client.login(username="teacher1", password="pass123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Teacher should see both courses created teacher_course and student_course
        self.assertContains(response, self.teacher_course.title)
        self.assertContains(response, self.student_course.title)
        self.assertContains(response, "Teacher status update")

    def test_student_public_profile(self):
        # Test the public profile view for students.
        url = reverse("accounts:public_profile", args=[self.student.username])
        self.client.login(username="teacher1", password="pass123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # For students display enrolled courses.
        self.assertNotContains(response, self.teacher_course.title)
        self.assertContains(response, self.student_course.title)
        self.assertContains(response, "Student status update")

    def test_search_results_link_to_public_profile(self):
        # Test that search results contain links to the public profile.
        self.client.login(username='teacher1', password='pass123')
        url = reverse("accounts:search_users") + "?q=teacher"
        response = self.client.get(url)
        teacher_profile_url = reverse("accounts:public_profile", args=[self.teacher.username])
        self.assertContains(response, teacher_profile_url)

    def test_base_template_contains_profile_link(self):
        # Test that the base template includes a link to the logged-in user's public profile.
        self.client.login(username="teacher1", password="pass123")
        response = self.client.get(reverse("accounts:home"))
        teacher_profile_url = reverse("accounts:public_profile", args=[self.teacher.username])
        self.assertContains(response, teacher_profile_url)
