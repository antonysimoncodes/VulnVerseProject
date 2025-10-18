from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def api_labs_index(request):
    """Display all available API lab templates"""
    return render(request, 'labs_api/api_labs_index.html', {'message': 'API Labs coming soon!'})
