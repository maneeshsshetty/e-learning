from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, CourseOffering, Enrollment

# --- USER ADMIN ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'otp', 'otp_created_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

# --- COURSE ADMIN ---
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'price', 'is_free', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_free', 'created_at')
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'teacher', 'photo')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free'),
            'description': 'Set course pricing. Mark as free or set a price in INR.'
        }),
    )

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'semester', 'year', 'created_at')
    list_filter = ('course', 'teacher', 'semester', 'year')
    search_fields = ('course__title', 'teacher__username')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'enrolled_at', 'grade')
    list_filter = ('course_offering__course', 'course_offering__semester')
    search_fields = ('student__username', 'course_offering__course__title')
