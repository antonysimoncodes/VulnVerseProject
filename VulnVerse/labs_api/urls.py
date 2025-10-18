from django.urls import path
from . import views

urlpatterns = [
    # API lab URLs will be added here
    path('', views.api_labs_index, name='api_labs_index'),
]