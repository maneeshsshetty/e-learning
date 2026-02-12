from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Enrollment, CustomUser, CourseContent, CourseOffering, Quiz, Question, Choice

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
        self.fields['teacher'].label_from_instance = lambda obj: f"{obj.username} ({obj.email})"

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('course_offering',)

class CourseOfferingForm(forms.ModelForm):
    class Meta:
        model = CourseOffering
        fields = ['course', 'semester', 'year']

class CourseContentForm(forms.ModelForm):
    class Meta:
        model = CourseContent
        fields = ['title', 'video', 'file', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lesson Title'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/...'}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'pass_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quiz Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Quiz Description'}),
            'pass_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Question Text'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choice Text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionWithChoicesForm(QuestionForm):
    choice_1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}))
    choice_2 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 2'}))
    choice_3 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 3 (Optional)'}))
    choice_4 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 4 (Optional)'}))
    correct_choice = forms.ChoiceField(
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')],
        widget=forms.RadioSelect(attrs={'class': 'list-style-none'}),
        initial='1'
    )

    class Meta(QuestionForm.Meta):
        fields = ['text', 'question_type', 'order', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_choice']
