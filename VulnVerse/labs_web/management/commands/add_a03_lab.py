from django.core.management.base import BaseCommand
from labs_web.models import LabTemplate

class Command(BaseCommand):
    help = 'Adds the A03 Injection lab to the database'

    def handle(self, *args, **options):
        # Check if the lab already exists
        if LabTemplate.objects.filter(lab_type='a03', name='SQL Injection Vulnerability Lab').exists():
            self.stdout.write(self.style.WARNING('A03 Injection lab already exists'))
            return
        
        # Create the lab template
        lab = LabTemplate.objects.create(
            name='SQL Injection Vulnerability Lab',
            description='Learn about SQL injection vulnerabilities by exploiting a vulnerable e-commerce application. '
                        'This lab demonstrates how improper input validation can lead to unauthorized data access '
                        'and manipulation through SQL injection attacks.',
            difficulty='beginner',
            lab_type='a03',
            docker_image='vulnverse_a03_injection',
            port_mapping='8003:5000',
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added A03 Injection lab: {lab}'))