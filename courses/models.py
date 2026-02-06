from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Course(models.Model):
    title = models.CharField(max_length=200) 
    description = models.TextField() 
    photo = models.ImageField(upload_to='course_photos/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teaching_courses', blank=True)

    def __str__(self):
        return self.title 

class CourseOffering(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_offerings')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    meet_link = models.URLField(blank=True, null=True) 
    class_description = models.TextField(blank=True, null=True, help_text="Specific details for this teacher's class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'course')

    def __str__(self):
        return f"{self.course.title} by {self.teacher.username}"

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments') 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments') 
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_enrollments') 
    enrolled_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ('student', 'course') 

    def __str__(self):
        return f"{self.student} -> {self.course} ({self.teacher})"
