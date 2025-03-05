from courses.models import Course
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import ChatMessage


@login_required
def course_chat_room(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Verify if the user is enrolled or is the teacher
    if request.user.role == 'student' and request.user not in course.enrolled_students.all():
        return render(request, "chat/forbidden.html", {"message": "You are not enrolled in this course."})

    # Retrieve chat history
    chat_history = ChatMessage.objects.filter(course=course).order_by('timestamp')

    return render(request, "chat/course_chat_room.html", {"course": course, "chat_history": chat_history})
