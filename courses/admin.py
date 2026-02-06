from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, CourseOffering, Enrollment

# --- USER ADMIN ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

# --- COURSE ADMIN ---
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'meet_link', 'created_at')
    list_filter = ('course', 'teacher')
    search_fields = ('course__title', 'teacher__username')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'teacher', 'enrolled_at')
    list_filter = ('course', 'teacher')
    search_fields = ('student__username', 'course__title', 'teacher__username')
