from django.urls import path
from . import views

urlpatterns = [
    path('', views.lesson_list, name='lessons'),
    path('log/', views.log_lesson, name='log_lesson'),
    path('bulk-log/', views.bulk_log_lessons, name='bulk_log_lessons'),  # Added missing URL pattern
]