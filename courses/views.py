from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Course, Enrollment, CourseOffering, CustomUser
from .forms import CourseForm, EnrollmentForm, CustomUserCreationForm
from django.contrib import messages


# ==============================================================================
# STANDARD VIEWS (THE PLATING CHEFS)
# ==============================================================================
# These views handle "Human" requests.
# They return HTML pages (templates) populated with data (context).
# ==============================================================================

def register(request):
    """
    Handles User Sign Up.
    """
    # 1. POST Request: User submitted the Sign Up form
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # Fill form with data
        if form.is_valid():
            user = form.save()          # Create User in DB
            login(request, user)        # Log them in automatically
            return redirect('dashboard') # Send to their dashboard
            
    # 2. GET Request: User just opened the page
    else:
        form = CustomUserCreationForm() # Create empty form
        
    # Render the HTML page with the form
    return render(request, 'registration/register.html', {'form': form})


@login_required # Security Guard: Must be logged in
def dashboard(request):
    """
    The Traffic Cop.
    Redirects users to their specific dashboard based on their role.
    """
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
        
    # Fallback if no specific role
    return render(request, 'dashboard/base_dashboard.html')


@login_required
def admin_dashboard(request):
    """
    Admin View: Manage Courses and View Users.
    API-DRIVEN LISTS: lists are fetched via JS.
    FORM-DRIVEN CREATION: Creation is still handled via standard Django POST for simplicity (file uploads).
    """
    # Security: Double check they are actually an admin
    if request.user.role != 'admin':
        return redirect('dashboard')

    # --- HANDLING COURSE CREATION (Standard Django Pattern) ---
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
    """
    Teacher View: Manage Classes and Opt-in to Courses.
    HYBRID: Lists fetched via API, but form submissions handled via standard POST
    """
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    # --- HANDLE FORM SUBMISSIONS ---
    if request.method == 'POST':
        # 1. Teacher wants to OPT-IN to teach a course
        if 'opt_in' in request.POST:
            course_id = request.POST.get('course_id')
            course = Course.objects.get(id=course_id)
            # Create a CourseOffering (teacher's class)
            CourseOffering.objects.create(teacher=request.user, course=course)
            messages.success(request, f'You are now teaching {course.title}!')
            return redirect('teacher_dashboard')
        
        # 2. Teacher wants to UPDATE class details (meet link, description)
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
    """
    Student View: See Enrolled Courses and Join New Ones.
    NOW API-DRIVEN: This view only serves the empty HTML shell.
    Data is fetched via JavaScript from /api/courses/ and /api/enrollments/
    """
    if request.user.role != 'student':
        return redirect('dashboard')
        
    return render(request, 'dashboard/student_dashboard.html')


@login_required
def student_course_detail(request, course_id):
    """
    Specific Page to see details of one Course and choose a Teacher.
    """
    if request.user.role != 'student':
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    offerings = CourseOffering.objects.filter(course=course) # All teachers teaching this course

    # Handle Enrollment Request
    if request.method == 'POST':
        offering_id = request.POST.get('offering_id')
        offering = get_object_or_404(CourseOffering, id=offering_id)
        teacher = offering.teacher
        
        # Prevent Double Enrollment
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, 'You are already enrolled in this course.')
        else:
            Enrollment.objects.create(student=request.user, course=course, teacher=teacher)
            messages.success(request, f'Enrolled in {course.title} with {teacher.username}!')
            return redirect('student_dashboard')
            
    return render(request, 'dashboard/student_course_detail.html', {'course': course, 'offerings': offerings})


# ==============================================================================
# API VIEWS EXPLAINED
# ==============================================================================
# API Views are for computer-to-computer communication.
# They don't return HTML pages; they return "pure data" (JSON).
# 
# REQUEST FLOW:
# 1. URL Request (e.g., GET /api/courses/) -> Comes here
# 2. ViewSet Checks Permissions (Is user allowed?)
# 3. ViewSet gets Data from Database (QuerySet)
# 4. ViewSet gives Data to Serializer (to convert to JSON)
# 5. Response sent back to user (JSON)
# ==============================================================================

from rest_framework import viewsets, permissions
from .serializers import CourseSerializer, EnrollmentSerializer, UserSerializer, CourseOfferingSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Supports filtering: /api/users/?role=teacher
    """
    queryset = CustomUser.objects.all() 
    serializer_class = UserSerializer
    # Changed from IsAdminUser to IsAuthenticated so our custom admin role can access
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Allows filtering by role (e.g. ?role=student)
        """
        queryset = CustomUser.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

class CourseOfferingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Teacher's Class Offerings.
    Supports filtering: /api/offerings/?teacher=ME
    """
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CourseOffering.objects.all()
        # Filter by teacher if requested (or default to current user if teacher)
        if self.request.user.role == 'teacher':
             queryset = queryset.filter(teacher=self.request.user)
        return queryset

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # IsAuthenticatedOrReadOnly: 
    # - Guests (Unauthenticated) can only READ (GET)
    # - Logged-in Users can READ and WRITE (POST, PUT, DELETE)
    # Note: In a real app, you might want only Teachers/Admins to write.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Enrollments (Who is in which course).
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    
    # IsAuthenticated: You MUST be logged in to see anything here.
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        """
        Custom Logic to filter what data a user sees.
        Overriding this method allows us to return different data for different users.
        """
        user = self.request.user
        
        # If student: Show only MY enrollments
        if user.role == 'student':
            return Enrollment.objects.filter(student=user)
            
        # If teacher: Show enrollments for courses I teach (optional logic)
        elif user.role == 'teacher':
             return Enrollment.objects.filter(teacher=user)
             
        # If Admin: Show everything
        return Enrollment.objects.all()
