from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Course, Enrollment, CourseOffering, CustomUser
from .forms import CourseForm, EnrollmentForm, CustomUserCreationForm
from django.contrib import messages

def register(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save() 
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, 'You are already enrolled in this course.')
        else:
            Enrollment.objects.create(student=request.user, course=course, teacher=teacher)
            messages.success(request, f'Enrolled in {course.title} with {teacher.username}!')
            return redirect('student_dashboard')
            
    return render(request, 'dashboard/student_course_detail.html', {'course': course, 'offerings': offerings})

from rest_framework import viewsets, permissions
from .serializers import CourseSerializer, EnrollmentSerializer, UserSerializer, CourseOfferingSerializer

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
             return Enrollment.objects.filter(teacher=user)
        return Enrollment.objects.all()
