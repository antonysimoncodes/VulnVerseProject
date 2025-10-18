from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('academy/', views.academy, name='academy'),
    path('blogs/', views.blogs, name='blogs'),
    path('profile/', views.profile_view, name='profile'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/list/', views.blog_list, name='blog_list'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:blog_id>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<int:blog_id>/delete/', views.blog_delete, name='blog_delete'),
    path('labs/', views.labs_view, name='labs'),
    path('labs/<int:lab_id>/', views.lab_detail, name='lab_detail'),
]
