from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, FeedbackForm, MaterialForm
from .models import Course, Feedback, Material, Notification

@login_required
def course_list(request):
    # Display list of courses, excluding blocked courses for students
    if request.user.role == 'student':
        courses = Course.objects.exclude(blocked_students=request.user)
    else:
        courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    # Display course details and materials if the user is enrolled or is the teacher
    course = get_object_or_404(Course, id=course_id)
    if request.user.role == 'student' and request.user not in course.enrolled_students.all():
        # Not enrolled so do not show materials.
        materials = []
    else:
        materials = course.materials.all()
    feedbacks = course.feedbacks.all()
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'feedbacks': feedbacks,
        'materials': materials
    })

@login_required
def add_course(request):
    # Allow teachers to add new courses
    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can add courses.")
        return redirect('courses:course_list')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Course added successfully.")
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'courses/add_course.html', {'form': form})

@login_required
def enroll_course(request, course_id):
    # Allow students to enroll in courses
    course = get_object_or_404(Course, id=course_id)
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('courses:course_detail', course_id=course.id)
    course.enrolled_students.add(request.user)
    messages.success(request, "Enrolled successfully.")
    return redirect('courses:course_detail', course_id=course.id)

@login_required
def add_feedback(request, course_id):
    # Allow students to leave feedback for a course
    course = get_object_or_404(Course, id=course_id)
    if request.user.role != 'student':
        messages.error(request, "Only students can leave feedback.")
        return redirect('courses:course_detail', course_id=course.id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.student = request.user
            feedback.save()
            messages.success(request, "Feedback submitted.")
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = FeedbackForm()
    return render(request, 'courses/add_feedback.html', {'form': form, 'course': course})

@login_required
def upload_material(request, course_id):
    # Allow teachers to upload materials for their courses
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        messages.error(request, "Only the teacher can upload materials for this course.")
        return redirect('courses:course_detail', course_id=course.id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, "Material uploaded successfully.")
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = MaterialForm()
    return render(request, 'courses/upload_material.html', {'form': form, 'course': course})

@login_required
def remove_student(request, course_id, student_id):
    # Allow teachers to remove students from their courses
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        messages.error(request, "Only the teacher can remove students.")
        return redirect('courses:course_detail', course_id=course.id)
    student = get_object_or_404(course.enrolled_students.model, id=student_id)
    course.enrolled_students.remove(student)
    Notification.objects.create(
        user=student,
        message=f"You have been removed from {course.title} by {request.user.username}."
    )
    messages.success(request, f"{student.username} has been removed from the course.")
    return redirect('courses:course_detail', course_id=course.id)

@login_required
def notifications(request):
    # Display notifications for the logged-in user
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'courses/notifications.html', {'notifications': user_notifications})

@login_required
def block_student(request, course_id, student_id):
    # Allow teachers to block students from their courses
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        messages.error(request, "Only the teacher can block students.")
        return redirect('courses:course_detail', course_id=course.id)
    student = get_object_or_404(course.enrolled_students.model, id=student_id)
    course.blocked_students.add(student)
    if student in course.enrolled_students.all():
        course.enrolled_students.remove(student)
    Notification.objects.create(
        user=student,
        message=f"You have been banned from {course.title} by {request.user.username}."
    )
    messages.success(request, f"{student.username} has been blocked from this course.")
    return redirect('courses:course_detail', course_id=course.id)

@login_required
def unblock_student(request, course_id, student_id):
    # Allow teachers to unblock students from their courses
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        messages.error(request, "Only the teacher can unban students.")
        return redirect('courses:course_detail', course_id=course.id)
    student = get_object_or_404(course.blocked_students.model, id=student_id)
    course.blocked_students.remove(student)
    messages.success(request, f"{student.username} has been unbanned from this course.")
    return redirect('courses:course_detail', course_id=course.id)
