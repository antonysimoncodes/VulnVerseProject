from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Blog, Lab, UserProfile
from .forms import BlogForm, UserProfileForm, CustomUserCreationForm, LoginForm

def landing_page(request):
    """Landing page view"""
    return render(request, 'landing.html')

@login_required
def academy(request):
    """Academy view - shows different lab categories"""
    return render(request, 'academy.html')

@login_required
def blogs(request):
    """Blogs view - redirect to blog list"""
    return redirect('blog_list')

def register_page(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to VulnVerse!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('landing_page')

def dashboard(request):
    """Dashboard view with user-specific content"""
    return render(request, 'dashboard.html')

@login_required
def profile_view(request):
    """View and edit user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
        'user_blogs': Blog.objects.filter(author=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'profile.html', context)

@login_required
def blog_create(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_list')
    else:
        form = BlogForm()
    
    return render(request, 'blog_create.html', {'form': form})

@login_required
def blog_list(request):
    """List all blog posts"""
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog_list.html', {'blogs': blogs})

@login_required
def blog_detail(request, blog_id):
    """View a specific blog post"""
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})

@login_required
def blog_edit(request, blog_id):
    """Edit a blog post"""
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Check if user owns the blog
    if blog.author != request.user:
        messages.error(request, 'You can only edit your own blog posts.')
        return redirect('blog_list')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog_detail', blog_id=blog.id)
    else:
        form = BlogForm(instance=blog)
    
    return render(request, 'blog_edit.html', {'form': form, 'blog': blog})

@login_required
def blog_delete(request, blog_id):
    """Delete a blog post"""
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Check if user owns the blog
    if blog.author != request.user:
        messages.error(request, 'You can only delete your own blog posts.')
        return redirect('blog_list')
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('blog_list')
    
    return render(request, 'blog_delete.html', {'blog': blog})

@login_required
def labs_view(request):
    """View available labs (login required)"""
    labs = Lab.objects.filter(is_available=True).order_by('difficulty_level')
    return render(request, 'labs.html', {'labs': labs})

@login_required
def lab_detail(request, lab_id):
    """View specific lab details"""
    lab = get_object_or_404(Lab, id=lab_id)
    return render(request, 'lab_detail.html', {'lab': lab})