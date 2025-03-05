# courses/urls.py
from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('add/', views.add_course, name='add_course'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('<int:course_id>/upload/', views.upload_material, name='upload_material'),
    path('<int:course_id>/remove_student/<int:student_id>/', views.remove_student, name='remove_student'),
    path('<int:course_id>/block_student/<int:student_id>/', views.block_student, name='block_student'),
    path('notifications/', views.notifications, name='notifications'),
    path('<int:course_id>/unblock_student/<int:student_id>/', views.unblock_student, name='unblock_student'),
]
