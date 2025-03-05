from django.contrib import admin

from .models import Course, Feedback, Material, Notification

admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Feedback)
admin.site.register(Notification)
