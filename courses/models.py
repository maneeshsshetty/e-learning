from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    # OTP Fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='courses_taught')
    photo = models.ImageField(upload_to='course_photos/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Course price in INR")
    is_free = models.BooleanField(default=False, help_text="Mark as free course")

    def __str__(self):
        return self.title
    
    def get_formatted_price(self):
        """Return formatted price with rupee symbol"""
        if self.is_free:
            return "FREE"
        return f"₹{self.price:,.2f}"

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='course_offerings')
    semester = models.CharField(max_length=20)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    meet_link = models.URLField(blank=True, null=True)
    class_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.semester} {self.year} ({self.teacher.username})"

class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='student_enrollment_set')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='offering_enrollment_set')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course_offering}"
