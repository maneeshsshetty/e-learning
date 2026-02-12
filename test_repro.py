
import os
import django
from django.conf import settings

# Configure settings manually (minimal)
settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'courses',
    ],
    SECRET_KEY='test',
)

django.setup()

from courses.models import CourseOffering, Quiz, Course, CustomUser

# Create dummy data
try:
    user = CustomUser.objects.create(username='testuser', role='teacher')
    course = Course.objects.create(title='Test Course', teacher=user)
    offering = CourseOffering.objects.create(
        course=course, teacher=user, semester='Fall', year=2023,
        start_date='2023-01-01', end_date='2023-12-31'
    )
    quiz = Quiz.objects.create(course_offering=offering, title='Test Quiz')
    
    # Simulate View Logic
    offerings = CourseOffering.objects.all().prefetch_related('quizzes')
    
    # Iterate and modify
    for off in offerings:
        off.quiz = off.quizzes.first()
        print(f"Inside view loop - Quiz ID: {off.quiz.id}")

    # Simulate Template Context
    # Template iterates over the SAME queryset object 'offerings'
    print("--- Template Simulation ---")
    for off in offerings:
        if hasattr(off, 'quiz'):
            print(f"Template loop - Quiz ID: {off.quiz.id}")
        else:
            print("Template loop - 'quiz' attribute MISSING!")

except Exception as e:
    print(f"Error: {e}")
