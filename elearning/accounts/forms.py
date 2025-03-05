from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, StatusUpdate

class CustomUserCreationForm(UserCreationForm):
    # Field for real name
    real_name = forms.CharField(max_length=100, required=True)
    # Field for user role
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    # Optional field for user photo
    photo = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        # Fields to include in the form
        fields = ('username', 'real_name', 'email', 'role', 'photo', 'password1', 'password2')

# Form for updating status
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        # Fields to include in the form
        fields = ['content']
