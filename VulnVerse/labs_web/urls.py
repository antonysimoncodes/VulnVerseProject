from django.urls import path
from . import views

urlpatterns = [
    path('', views.labs_index, name='labs_index'),
    path('template/<int:template_id>/', views.lab_detail, name='lab_detail'),
    path('template/<int:template_id>/start/', views.start_lab, name='start_lab'),
    path('instance/<int:instance_id>/', views.lab_instance, name='lab_instance'),
    path('instance/<int:instance_id>/stop/', views.stop_lab, name='stop_lab'),
    path('instance/<int:instance_id>/reset/', views.reset_lab, name='reset_lab'),
    # ...existing code...
]

        