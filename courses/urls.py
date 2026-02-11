from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/courses/', views.available_courses, name='available_courses'),
    path('dashboard/student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('dashboard/student/course/<int:course_id>/content/', views.course_content_view, name='course_content_view'),
    path('payment/course/<int:course_id>/', views.course_payment_page, name='course_payment_page'),
    path('payment/<int:offering_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('payment/paypal/execute/', views.paypal_execute, name='paypal_execute'),
    path('payment/paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),

    # Quiz URLs
    path('dashboard/teacher/offering/<int:offering_id>/add_quiz/', views.add_quiz, name='add_quiz'),
    path('dashboard/teacher/quiz/<int:quiz_id>/manage/', views.manage_quiz, name='manage_quiz'),
    path('dashboard/teacher/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('dashboard/teacher/quiz/<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('dashboard/teacher/question/<int:question_id>/add_choice/', views.add_choice, name='add_choice'),
    path('dashboard/teacher/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('dashboard/teacher/choice/<int:choice_id>/delete/', views.delete_choice, name='delete_choice'),
    
    path('dashboard/student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('dashboard/student/quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('dashboard/student/quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),
]
