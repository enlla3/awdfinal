from django import forms

from .models import Course, Feedback, Material


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['file']
