from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # third-party
    path("__reload__/", include("django_browser_reload.urls")),
    
    # admin
    path('admin/', admin.site.urls),
    
    #apps
    path('', include('users.urls')),
    path('students/', include('students.urls')),
    path('lessons/', include('lessons.urls')),
    path('invoices/', include('invoices.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)