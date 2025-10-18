from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

class LabTemplate(models.Model):
    """Model representing a lab template that can be instantiated"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    LAB_TYPE_CHOICES = [
        ('a01', 'A01: Broken Access Control'),
        ('a02', 'A02: Cryptographic Failures'),
        ('a03', 'A03: Injection'),
        ('a04', 'A04: Insecure Design'),
        ('a05', 'A05: Security Misconfiguration'),
        ('a06', 'A06: Vulnerable Components'),
        ('a07', 'A07: Auth & Identification Failures'),
        ('a08', 'A08: Software & Data Integrity Failures'),
        ('a09', 'A09: Security Logging & Monitoring Failures'),
        ('a10', 'A10: Server-Side Request Forgery'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    lab_type = models.CharField(max_length=20, choices=LAB_TYPE_CHOICES)
    docker_image = models.CharField(max_length=255, help_text="Docker image name for this lab")
    port_mapping = models.CharField(max_length=50, help_text="Port mapping for the container (e.g., '8080:80')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_lab_type_display()} - {self.name}"

class LabInstance(models.Model):
    """Model representing a running instance of a lab template"""
    STATUS_CHOICES = [
        ('creating', 'Creating'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
    ]
    
    template = models.ForeignKey(LabTemplate, on_delete=models.CASCADE, related_name='instances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_instances')
    container_id = models.CharField(max_length=100, blank=True, null=True)
    instance_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='creating')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    access_url = models.URLField(blank=True, null=True, help_text="URL to access the lab instance")
    
    def __str__(self):
        return f"{self.template.name} - {self.user.username} - {self.status}"
    
    def start(self):
        """Start the lab instance"""
        self.status = 'running'
        self.started_at = datetime.now()
        self.stopped_at = None
        self.save()
    
    def stop(self):
        """Stop the lab instance"""
        self.status = 'stopped'
        self.stopped_at = datetime.now()
        self.save()
    
    def reset(self):
        """Reset the lab instance"""
        self.stop()
        self.start()
