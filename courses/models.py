from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary_storage.storage import VideoMediaCloudinaryStorage, RawMediaCloudinaryStorage
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='courses_taught', blank=True, null=True)
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

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_METHOD = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    )
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    

    paypal_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_payer_id = models.CharField(max_length=100, blank=True, null=True)
    payment_source = models.CharField(max_length=20, default='dummy', choices=(('paypal', 'PayPal'), ('dummy', 'Dummy')))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        course_title = self.course.title if self.course else self.course_offering.course.title
        return f"{self.student.username} - {course_title} - ₹{self.amount} ({self.status})"

class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='student_enrollment_set')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='offering_enrollment_set')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course_offering}"

class CourseContent(models.Model):
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    
    video = models.FileField(
        upload_to='course_videos/', 
        blank=True, 
        null=True,
        storage=VideoMediaCloudinaryStorage(),
        help_text="Upload course video"
    )
    

    file = models.FileField(
        upload_to='course_files/', 
        blank=True, 
        null=True,
        storage=RawMediaCloudinaryStorage(),
        help_text="Upload PDF or resource file"
    )
    

    link = models.URLField(blank=True, null=True, help_text="External link (e.g., Google Meet)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course_offering.course.title})"

class Quiz(models.Model):
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    pass_percentage = models.FloatField(default=50.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course_offering}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('single_choice', 'Single Choice'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class StudentQuizAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField()
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}%"

class Certificate(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    file = models.FileField(upload_to='certificates/', blank=True, null=True, storage=RawMediaCloudinaryStorage())

    def __str__(self):
        return f"Certificate for {self.student.username} - {self.course_offering}"
