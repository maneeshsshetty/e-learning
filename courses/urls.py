from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    # path('verify-otp/', views.verify_otp, name='verify_otp'),  # DISABLED: No longer using OTP
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/courses/', views.available_courses, name='available_courses'),
    path('dashboard/student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('payment/course/<int:course_id>/', views.course_payment_page, name='course_payment_page'),
    path('payment/<int:offering_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('payment/paypal/execute/', views.paypal_execute, name='paypal_execute'),
    path('payment/paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
]
