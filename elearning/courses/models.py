from django.conf import settings
from django.contrib.auth import get_user_model
# courses/models.py
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    enrolled_students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)
    blocked_students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='blocked_courses', blank=True)

    def __str__(self):
        return self.title

# Course Material
class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Material for {self.course.title}"

# Feedback model
class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student.username} on {self.course.title}"

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

# Notify teacher when a student enrolls in a course
@receiver(m2m_changed, sender=Course.enrolled_students.through)
def notify_teacher_on_enrollment(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            student = get_user_model().objects.get(pk=pk)
            teacher = instance.teacher
            Notification.objects.create(
                user=teacher,
                message=f"Student {student.username} enrolled in {instance.title}."
            )

# Notify enrolled students when new material is added
@receiver(post_save, sender=Material)
def notify_students_on_material(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.enrolled_students.all():
            Notification.objects.create(
                user=student,
                message=f"New material added to {course.title}."
            )
