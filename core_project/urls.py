from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ==============================================================================
# 1. THE MAIN DOOR (Project URLs)
# ==============================================================================
# This is the first place a request lands.
# It decides if the request is for the Admin Panel, the Web App, or the API.
# ==============================================================================

from rest_framework.routers import DefaultRouter
from courses.views import UserViewSet, CourseViewSet, EnrollmentViewSet, CourseOfferingViewSet

# ROUTER: This automatically creates API URLs for us
# e.g., 'api/users/', 'api/users/1/', 'api/courses/' ...
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'offerings', CourseOfferingViewSet) # New Endpoint for Teachers

urlpatterns = [
    # 1. Django Admin (Superuser control panel)
    path('django_admin/', admin.site.urls),
    
    # 2. The Web App (HTML Pages) -> Goes to courses/urls.py
    path('', include('courses.urls')),
    
    # 3. The API (JSON Data for Apps) -> Goes to the Router -> ViewSets
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
