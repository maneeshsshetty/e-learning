from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Course, CourseOffering, CustomUser, Enrollment
from .forms import CourseForm, EnrollmentForm, CustomUserCreationForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth import get_user_model

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until OTP is verified
            
            # Generate 6-digit OTP
            import random
            from django.utils import timezone
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Send OTP via email
            mail_subject = 'Verify your account - OTP Code'
            message = f"""
Hello {user.username},

Thank you for registering! Please use the following OTP code to verify your account:

OTP Code: {otp}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
Learning Platform Team
"""
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            
            # Store user ID in session for OTP verification
            request.session['pending_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        user_id = request.session.get('pending_user_id')
        
        if not user_id:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')
        
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, 'Invalid session. Please register again.')
            return redirect('register')
        
        # Check if OTP matches
        if user.otp != otp_entered:
            messages.error(request, 'Invalid OTP code. Please try again.')
            return render(request, 'registration/verify_otp.html')
        
        # Check if OTP has expired (10 minutes)
        from django.utils import timezone
        from datetime import timedelta
        if user.otp_created_at:
            # Make sure both datetimes are timezone-aware for comparison
            otp_created = user.otp_created_at
            if timezone.is_naive(otp_created):
                otp_created = timezone.make_aware(otp_created)
            
            expiry_time = otp_created + timedelta(minutes=10)
            if timezone.now() > expiry_time:
                messages.error(request, 'OTP has expired. Please register again.')
                user.delete()  # Clean up expired registration
                return redirect('register')
        
        # OTP is valid - activate user
        user.is_active = True
        user.otp = None  # Clear OTP
        user.otp_created_at = None
        user.save()
        
        # Clear session
        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Your account has been verified successfully!')
        return redirect('dashboard')
    
    return render(request, 'registration/verify_otp.html')


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    return render(request, 'dashboard/base_dashboard.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('admin_dashboard')
    else:
        form = CourseForm()
        
    return render(request, 'dashboard/admin_dashboard.html', {'form': form})

@login_required 
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    if request.method == 'POST':
        if 'opt_in' in request.POST:
            course_id = request.POST.get('course_id')
            course = Course.objects.get(id=course_id)
            CourseOffering.objects.create(teacher=request.user, course=course)
            messages.success(request, f'You are now teaching {course.title}!')
            return redirect('teacher_dashboard')
        elif 'update_details' in request.POST:
            offering_id = request.POST.get('offering_id')
            offering = CourseOffering.objects.get(id=offering_id, teacher=request.user)
            offering.meet_link = request.POST.get('meet_link')
            offering.class_description = request.POST.get('class_description')
            offering.save()
            messages.success(request, 'Class details updated!')
            return redirect('teacher_dashboard')
    return render(request, 'dashboard/teacher_dashboard.html')

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    return render(request, 'dashboard/student_dashboard.html')

@login_required
def student_course_detail(request, course_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    course = get_object_or_404(Course, id=course_id)
    offerings = CourseOffering.objects.filter(course=course)
    if request.method == 'POST':
        offering_id = request.POST.get('offering_id')
        offering = get_object_or_404(CourseOffering, id=offering_id)
        teacher = offering.teacher
        if Enrollment.objects.filter(student=request.user, course_offering=offering).exists():
            messages.warning(request, 'You are already enrolled in this course offering.')
        else:
            Enrollment.objects.create(student=request.user, course_offering=offering)
            messages.success(request, f'Successfully enrolled in {course.title}!')
            return redirect('student_dashboard')
            
    return render(request, 'dashboard/student_course_detail.html', {'course': course, 'offerings': offerings})

from rest_framework import viewsets, permissions
from .serializers import CourseSerializer, UserSerializer, CourseOfferingSerializer, EnrollmentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all() 
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

class CourseOfferingViewSet(viewsets.ModelViewSet):
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CourseOffering.objects.all()
        if self.request.user.role == 'teacher':
             queryset = queryset.filter(teacher=self.request.user)
        return queryset

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Enrollment.objects.filter(student=user)
        elif user.role == 'teacher':
             return Enrollment.objects.filter(course_offering__teacher=user)
        return Enrollment.objects.all()
