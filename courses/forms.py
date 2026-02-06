from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Enrollment, CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description', 'photo')

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('course', 'teacher')
