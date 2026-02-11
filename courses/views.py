from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Course, CourseOffering, CustomUser, Enrollment, CourseContent, Quiz, Question, Choice, StudentQuizAttempt, Certificate
from .forms import CourseForm, EnrollmentForm, CustomUserCreationForm, CourseContentForm, QuizForm, QuestionForm, ChoiceForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.conf import settings
from .brevo_email import send_brevo_email

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require OTP verification
            
            # Generate 6-digit OTP
            import random
            from django.utils import timezone
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            
            # Send OTP email using Brevo API
            context = {
                'username': user.username,
                'otp': otp,
            }
            html_message = render_to_string('emails/otp_verification.html', context)
            
            # Send email
            result = send_brevo_email(
                to_email=user.email,
                subject='Verify Your Email - Learning Platform',
                html_content=html_message
            )
            
            if result['success']:
                # Store user ID in session for OTP verification
                request.session['pending_user_id'] = user.id
                messages.success(request, f'Registration successful! Please check your email ({user.email}) for the OTP code.')
                return redirect('verify_otp')
            else:
                # If email fails, delete the user and show error
                user.delete()
                messages.error(request, f'Failed to send verification email: {result["message"]}')
                return redirect('register')
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
        
        # Send welcome email using Brevo API
        context = {
            'username': user.username,
            'role': user.role,
            'dashboard_url': request.build_absolute_uri('/dashboard/'),
        }
        html_message = render_to_string('emails/welcome.html', context)
        
        try:
            result = send_brevo_email(
                to_email=user.email,
                subject='Welcome to Learning Platform!',
                html_content=html_message
            )
            if not result['success']:
                print(f"Failed to send welcome email: {result['message']}")
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
        
        # Clear session
        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Your account has been verified successfully! Welcome to Learning Platform.')
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
    
    # Get all offerings for this teacher
    offerings = CourseOffering.objects.filter(teacher=request.user)
    
    if request.method == 'POST':
        if 'opt_in' in request.POST:
            course_id = request.POST.get('course_id')
            course = Course.objects.get(id=course_id)
            CourseOffering.objects.create(teacher=request.user, course=course)
            messages.success(request, f'You are now teaching {course.title}!')
            return redirect('teacher_dashboard')
            
        elif 'update_details' in request.POST:
            offering_id = request.POST.get('offering_id')
            offering = get_object_or_404(CourseOffering, id=offering_id, teacher=request.user)
            offering.meet_link = request.POST.get('meet_link')
            offering.class_description = request.POST.get('class_description')
            offering.save()
            messages.success(request, 'Class details updated!')
            return redirect('teacher_dashboard')
            
        elif 'add_content' in request.POST:
            offering_id = request.POST.get('offering_id')
            offering = get_object_or_404(CourseOffering, id=offering_id, teacher=request.user)
            
            form = CourseContentForm(request.POST, request.FILES)
            if form.is_valid():
                content = form.save(commit=False)
                content.course_offering = offering
                content.save()
                messages.success(request, 'Content added successfully!')
            else:
                messages.error(request, 'Error adding content. Please check the form.')
            return redirect('teacher_dashboard')
            
        elif 'delete_content' in request.POST:
            content_id = request.POST.get('content_id')
            content = get_object_or_404(CourseContent, id=content_id, course_offering__teacher=request.user)
            content.delete()
            messages.success(request, 'Content deleted successfully!')
            return redirect('teacher_dashboard')

    return render(request, 'dashboard/teacher_dashboard.html', {'offerings': offerings})

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    return render(request, 'dashboard/student_dashboard.html')

@login_required
def available_courses(request):
    return render(request, 'dashboard/available_courses.html')

@login_required
def student_course_detail(request, course_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    course = get_object_or_404(Course, id=course_id)
    offerings = CourseOffering.objects.filter(course=course)
    
    # Check if user has already paid for this course
    has_paid = Payment.objects.filter(
        student=request.user,
        course=course,
        status='success'
    ).exists()

    # Check if user is enrolled in ANY offering of this course
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course_offering__course=course
    ).exists()
    
    # Grant access if paid OR enrolled
    has_access = has_paid or is_enrolled
    
    if request.method == 'POST':
        offering_id = request.POST.get('offering_id')
        offering = get_object_or_404(CourseOffering, id=offering_id)
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course_offering=offering).exists():
            messages.warning(request, 'You are already enrolled in this course offering.')
        else:
            # Check if course is free OR user has already paid
            if course.is_free or course.price == 0 or has_paid:
                # Free course or already paid - direct enrollment
                payment = None
                if has_paid:
                    # Link to existing payment
                    payment = Payment.objects.filter(
                        student=request.user,
                        course=course,
                        status='success'
                    ).first()
                    # Update payment to link to this offering
                    if payment and not payment.course_offering:
                        payment.course_offering = offering
                        payment.save()
                
                Enrollment.objects.create(
                    student=request.user,
                    course_offering=offering,
                    payment=payment
                )
                messages.success(request, f'Successfully enrolled in {course.title} with {offering.teacher.username}!')
                return redirect('student_dashboard')
            else:
                # Paid course and hasn't paid yet - redirect to payment
                return redirect('course_payment_page', course_id=course.id)
            
    return render(request, 'dashboard/student_course_detail.html', {
        'course': course,
        'offerings': offerings,
        'has_paid': has_paid,
        'is_enrolled': is_enrolled,
        'has_access': has_access
    })

@login_required
def course_content_view(request, course_id):
    if request.user.role != 'student':
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    
    # Check access (Paid OR Enrolled)
    has_paid = Payment.objects.filter(student=request.user, course=course, status='success').exists()
    is_enrolled = Enrollment.objects.filter(student=request.user, course_offering__course=course).exists()
    
    if not (has_paid or is_enrolled):
        messages.error(request, 'You need to enroll in this course to view content.')
        return redirect('student_course_detail', course_id=course.id)
    
    offerings = CourseOffering.objects.filter(course=course).prefetch_related('contents', 'quizzes')
    
    # Calculate total content count
    contents_count = sum(offering.contents.count() for offering in offerings)

    # Attach quiz info to offerings
    for offering in offerings:
        offering.quiz = offering.quizzes.first()
        if offering.quiz:
            offering.attempt = StudentQuizAttempt.objects.filter(student=request.user, quiz=offering.quiz).order_by('-completed_at').first()
    
    return render(request, 'dashboard/course_content.html', {
        'course': course,
        'offerings': offerings,
        'contents_count': contents_count
    })

@login_required
def course_payment_page(request, course_id):
    """Payment page for course-level payments (not tied to specific teacher)"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already paid for this course
    existing_payment = Payment.objects.filter(
        student=request.user,
        course=course,
        status='success'
    ).first()
    
    if existing_payment:
        messages.info(request, 'You have already paid for this course. Please select your teacher.')
        return redirect('student_course_detail', course_id=course.id)
    
    if request.method == 'POST':
        # PayPal Payment Only
        from .paypal_service import create_payment
        from django.urls import reverse
        
        # Build absolute URLs for PayPal redirect
        return_url = request.build_absolute_uri(reverse('paypal_execute'))
        cancel_url = request.build_absolute_uri(reverse('paypal_cancel'))
        
        # Create PayPal payment
        result = create_payment(
            amount=course.price,
            currency='USD',  # Change to 'INR' if needed
            return_url=return_url,
            cancel_url=cancel_url,
            description=f"{course.title} - Course Access"
        )
        
        if result['success']:
            # Store payment info in session
            request.session['pending_payment'] = {
                'course_id': course.id,  # Changed from offering_id
                'paypal_payment_id': result['payment_id'],
                'amount': str(course.price)
            }
            # Redirect to PayPal for approval
            return redirect(result['approval_url'])
        else:
            messages.error(request, f"PayPal payment creation failed: {result['error']}")
            return redirect('course_payment_page', course_id=course.id)
    
    return render(request, 'payment/payment.html', {
        'course': course,
        'amount': course.price
    })

@login_required
def payment_page(request, offering_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    offering = get_object_or_404(CourseOffering, id=offering_id)
    course = offering.course
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course_offering=offering).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('student_dashboard')
    
    # Check if already paid
    existing_payment = Payment.objects.filter(
        student=request.user, 
        course_offering=offering,
        status='success'
    ).first()
    
    if existing_payment:
        messages.info(request, 'Payment already completed for this course.')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        # PayPal Payment Only
        from .paypal_service import create_payment
        from django.urls import reverse
        
        # Build absolute URLs for PayPal redirect
        return_url = request.build_absolute_uri(reverse('paypal_execute'))
        cancel_url = request.build_absolute_uri(reverse('paypal_cancel'))
        
        # Create PayPal payment
        result = create_payment(
            amount=course.price,
            currency='USD',  # Change to 'INR' if needed
            return_url=return_url,
            cancel_url=cancel_url,
            description=f"{course.title} - {offering.semester} {offering.year}"
        )
        
        if result['success']:
            # Store payment info in session
            request.session['pending_payment'] = {
                'offering_id': offering.id,
                'paypal_payment_id': result['payment_id'],
                'amount': str(course.price)
            }
            # Redirect to PayPal for approval
            return redirect(result['approval_url'])
        else:
            messages.error(request, f"PayPal payment creation failed: {result['error']}")
            return redirect('payment_page', offering_id=offering.id)
    
    return render(request, 'payment/payment.html', {
        'offering': offering,
        'course': course,
        'amount': course.price
    })



@login_required
def payment_success(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id, student=request.user)
    return render(request, 'payment/payment_success.html', {'payment': payment})


@login_required
def paypal_execute(request):
    """Handle PayPal return after user approves payment"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # Get PayPal parameters
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    # Get pending payment from session
    pending_payment = request.session.get('pending_payment')
    
    if not pending_payment or not payment_id or not payer_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('student_dashboard')
    
    # Execute PayPal payment
    from .paypal_service import execute_payment
    result = execute_payment(payment_id, payer_id)
    
    if result['success']:
        import uuid
        transaction_id = f"PAYPAL{uuid.uuid4().hex[:10].upper()}"
        
        # Check if this is a course-level payment (new flow) or offering-level (old flow)
        if 'course_id' in pending_payment:
            # NEW FLOW: Course-level payment
            course = get_object_or_404(Course, id=pending_payment['course_id'])
            
            payment = Payment.objects.create(
                student=request.user,
                course=course,
                course_offering=None,  # No offering yet - student will select teacher
                amount=pending_payment['amount'],
                payment_method='paypal',
                status='success',
                transaction_id=transaction_id,
                payment_source='paypal',
                paypal_payment_id=payment_id,
                paypal_payer_id=payer_id
            )
            
            # Clear session
            del request.session['pending_payment']
            
            messages.success(request, 'Payment completed successfully! Now select your teacher.')
            return redirect('student_course_detail', course_id=course.id)
            
        else:
            # OLD FLOW: Offering-level payment (backward compatibility)
            offering = get_object_or_404(CourseOffering, id=pending_payment['offering_id'])
            
            payment = Payment.objects.create(
                student=request.user,
                course=offering.course,
                course_offering=offering,
                amount=pending_payment['amount'],
                payment_method='paypal',
                status='success',
                transaction_id=transaction_id,
                payment_source='paypal',
                paypal_payment_id=payment_id,
                paypal_payer_id=payer_id
            )
            
            # Create enrollment
            Enrollment.objects.create(
                student=request.user,
                course_offering=offering,
                payment=payment
            )
            
            # Clear session
            del request.session['pending_payment']
            
            messages.success(request, 'Payment completed successfully via PayPal!')
            return redirect('payment_success', transaction_id=transaction_id)
    else:
        messages.error(request, f'Payment execution failed: {result["error"]}')
        return redirect('student_dashboard')



@login_required
def paypal_cancel(request):
    """Handle PayPal cancellation"""
    if 'pending_payment' in request.session:
        del request.session['pending_payment']
    
    messages.warning(request, 'Payment was cancelled.')
    return redirect('student_dashboard')


from rest_framework import viewsets, permissions, filters
from .models import Payment
from .serializers import CourseSerializer, UserSerializer, CourseOfferingSerializer, EnrollmentSerializer, PaymentSerializer

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
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Payment.objects.filter(student=user)
        return Payment.objects.all()
    
    def perform_create(self, serializer):
        # Save payment
        payment = serializer.save()
        
        # Auto-create enrollment after successful payment
        if payment.status == 'success':
            Enrollment.objects.create(
                student=payment.student,
                course_offering=payment.course_offering,
                payment=payment
            )

# Quiz Views - Teacher

@login_required
def add_quiz(request, offering_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    offering = get_object_or_404(CourseOffering, id=offering_id, teacher=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course_offering = offering
            quiz.save()
            messages.success(request, 'Quiz created successfully! Now add questions.')
            return redirect('manage_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'courses/quiz_form.html', {'form': form, 'offering': offering})

@login_required
def manage_quiz(request, quiz_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, course_offering__teacher=request.user)
    
    return render(request, 'courses/manage_quiz.html', {'quiz': quiz})

@login_required
def delete_quiz(request, quiz_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
        
    quiz = get_object_or_404(Quiz, id=quiz_id, course_offering__teacher=request.user)
    offering_id = quiz.course_offering.id
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully.')
    return redirect('teacher_dashboard')

@login_required
def add_question(request, quiz_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id, course_offering__teacher=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added! Now add choices.')
            return redirect('manage_quiz', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    return render(request, 'courses/question_form.html', {'form': form, 'quiz': quiz})

@login_required
def add_choice(request, question_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    question = get_object_or_404(Question, id=question_id, quiz__course_offering__teacher=request.user)
    
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            messages.success(request, 'Choice added!')
            return redirect('manage_quiz', quiz_id=question.quiz.id)
    else:
        form = ChoiceForm()
    


    return render(request, 'courses/choice_form.html', {'form': form, 'question': question})

@login_required
def delete_question(request, question_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    question = get_object_or_404(Question, id=question_id, quiz__course_offering__teacher=request.user)
    quiz_id = question.quiz.id
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('manage_quiz', quiz_id=quiz_id)

@login_required
def delete_choice(request, choice_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    choice = get_object_or_404(Choice, id=choice_id, question__quiz__course_offering__teacher=request.user)
    quiz_id = choice.question.quiz.id
    choice.delete()
    messages.success(request, 'Choice deleted.')
    return redirect('manage_quiz', quiz_id=quiz_id)

# Quiz Views - Student

@login_required
def take_quiz(request, quiz_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check enrollment
    is_enrolled = Enrollment.objects.filter(student=request.user, course_offering=quiz.course_offering).exists()
    if not is_enrolled:
        messages.error(request, 'You need to be enrolled to take this quiz.')
        return redirect('student_dashboard')

    questions = quiz.questions.all()
    
    return render(request, 'courses/take_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def submit_quiz(request, quiz_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_questions = questions.count()
    correct_answers = 0
    
    if request.method == 'POST':
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = Choice.objects.get(id=selected_choice_id)
                if choice.is_correct:
                    correct_answers += 1
        
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = score_percentage >= quiz.pass_percentage
        
        # Save attempt
        attempt = StudentQuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=score_percentage,
            passed=passed
        )
        
        # Generate Certificate if passed
        if passed:
            if not Certificate.objects.filter(student=request.user, course_offering=quiz.course_offering).exists():
                Certificate.objects.create(
                    student=request.user,
                    course_offering=quiz.course_offering
                )
        
        return redirect('quiz_result', attempt_id=attempt.id)
    
    return redirect('take_quiz', quiz_id=quiz.id)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id, student=request.user)
    certificate = None
    if attempt.passed:
        certificate = Certificate.objects.filter(student=request.user, course_offering=attempt.quiz.course_offering).first()
        
    return render(request, 'courses/quiz_result.html', {'attempt': attempt, 'certificate': certificate})

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)
    
    template_path = 'courses/certificate_pdf.html'
    context = {'certificate': certificate}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.student.username}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
