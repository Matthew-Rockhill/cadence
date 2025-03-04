from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='students'),
    path('add/', views.add_student, name='add_student'),
]