from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import LabTemplate, LabInstance
from .docker_service import docker_service

@login_required
def labs_index(request):
    """Display all available lab templates"""
    templates = LabTemplate.objects.filter(is_active=True).order_by('lab_type')
    
    # Get user's active lab instances
    user_instances = LabInstance.objects.filter(
        user=request.user,
        status__in=['creating', 'running']
    )
    
    context = {
        'lab_templates': templates,
        'active_instances': user_instances,
    }
    
    return render(request, 'labs_web/labs_index.html', context)

@login_required
def lab_detail(request, template_id):
    """Display details for a specific lab template"""
    template = get_object_or_404(LabTemplate, id=template_id, is_active=True)
    
    # Check if user already has an instance of this lab
    try:
        instance = LabInstance.objects.get(
            user=request.user,
            template=template,
            status__in=['creating', 'running']
        )
        has_active_instance = True
    except LabInstance.DoesNotExist:
        instance = None
        has_active_instance = False
    
    context = {
        'template': template,
        'instance': instance,
        'has_active_instance': has_active_instance,
    }
    
    return render(request, 'labs_web/lab_detail.html', context)

@login_required
def start_lab(request, template_id):
    """Start a new lab instance"""
    if request.method != 'POST':
        return redirect('labs_index')
    
    template = get_object_or_404(LabTemplate, id=template_id, is_active=True)
    
    # Check if user already has an active instance of this lab
    existing_instance = LabInstance.objects.filter(
        user=request.user,
        template=template,
        status__in=['creating', 'running']
    ).first()
    
    if existing_instance:
        messages.info(request, f'You already have an active instance of {template.name}')
        return redirect('lab_instance', instance_id=existing_instance.id)
    
    # Create a new lab instance
    instance = LabInstance.objects.create(
        template=template,
        user=request.user,
        status='creating'
    )

    # Start the Docker container
    success = docker_service.create_container(instance)


    import logging
    logger = logging.getLogger(__name__)
    if success:
        instance.start()
        instance.save()
        logger.info(f"Lab started. Access URL: {instance.access_url}, Container ID: {instance.container_id}")
        messages.success(request, f'Lab {template.name} started successfully!')
        # Redirect to the lab instance page so template logic and auto-open work
        return redirect('lab_instance', instance_id=instance.id)
    else:
        instance.status = 'error'
        instance.save()
        messages.error(request, f'Failed to start lab {template.name}. Please try again later.')
        return redirect('lab_instance', instance_id=instance.id)

@login_required
def stop_lab(request, instance_id):
    """Stop a running lab instance"""
    if request.method != 'POST':
        return redirect('labs_index')
    
    instance = get_object_or_404(LabInstance, id=instance_id, user=request.user)
    
    if instance.status != 'running':
        messages.info(request, f'Lab instance is not running')
        return redirect('lab_instance', instance_id=instance.id)
    
    # Stop the Docker container
    success = docker_service.stop_container(instance)
    
    if success:
        messages.success(request, f'Lab {instance.template.name} stopped successfully!')
    else:
        messages.error(request, f'Failed to stop lab {instance.template.name}. Please try again later.')
    
    return redirect('lab_instance', instance_id=instance.id)

@login_required
def reset_lab(request, instance_id):
    """Reset a lab instance"""
    if request.method != 'POST':
        return redirect('labs_index')
    
    instance = get_object_or_404(LabInstance, id=instance_id, user=request.user)
    
    # Reset the Docker container
    success = docker_service.reset_container(instance)
    
    if success:
        messages.success(request, f'Lab {instance.template.name} reset successfully!')
    else:
        messages.error(request, f'Failed to reset lab {instance.template.name}. Please try again later.')
    
    return redirect('lab_instance', instance_id=instance.id)

@login_required
def lab_instance(request, instance_id):
    """Display details for a specific lab instance"""
    instance = get_object_or_404(LabInstance, id=instance_id, user=request.user)
    
    # Sync container status with Docker
    if instance.container_id:
        docker_service.sync_container_status(instance)
        
        # If instance is in error state but container exists and is running, force it to running state
        if instance.status == 'error' and instance.access_url:
            instance.status = 'running'
            instance.save()
    
    context = {
        'instance': instance,
        'template': instance.template,
    }
    
    return render(request, 'labs_web/lab_instance.html', context)
