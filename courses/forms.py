from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Enrollment, CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role')

class CourseForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='teacher'),
        required=False,
        empty_label="Select a teacher (optional)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Choose the teacher for this course (optional)"
    )
    
    class Meta:
        model = Course
        fields = ('title', 'description', 'teacher', 'price', 'is_free', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter course description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'price': 'Course price in INR (₹)',
            'is_free': 'Check this box to make the course free',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the teacher field label to show username and email
        self.fields['teacher'].label_from_instance = lambda obj: f"{obj.username} ({obj.email})"

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('course_offering',)
