import docker
import logging
from django.conf import settings
from .models import LabInstance

logger = logging.getLogger(__name__)

class DockerService:
    """Service for managing Docker containers for lab instances"""
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.client = None
    
    def create_container(self, lab_instance):
        """Create a Docker container for a lab instance"""
        if not self.client:
            logger.error("Docker client not initialized")
            return False
        
        try:
            # Get the lab template
            template = lab_instance.template
            
            # Parse port mapping
            host_port, container_port = template.port_mapping.split(':')
            port_mapping = {container_port: int(host_port)}
            
            # Create a unique name for the container
            container_name = f"lab-{template.lab_type}-{lab_instance.instance_uuid}"
            
            # Create the container
            container = self.client.containers.run(
                image=template.docker_image,
                name=container_name,
                detach=True,
                ports=port_mapping,
                restart_policy={"Name": "unless-stopped"},
                network="vulnverse_labs",  # Isolated network for labs
            )
            
            # Update the lab instance with container info
            lab_instance.container_id = container.id
            lab_instance.access_url = f"http://localhost:{host_port}"
            lab_instance.save()
            
            logger.info(f"Container created: {container_name} ({container.id})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create container: {str(e)}")
            lab_instance.status = 'error'
            lab_instance.save()
            return False
    
    def start_container(self, lab_instance):
        """Start a Docker container for a lab instance"""
        if not self.client or not lab_instance.container_id:
            return False
        
        try:
            container = self.client.containers.get(lab_instance.container_id)
            container.start()
            lab_instance.start()
            logger.info(f"Container started: {lab_instance.container_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start container: {str(e)}")
            lab_instance.status = 'error'
            lab_instance.save()
            return False
    
    def stop_container(self, lab_instance):
        """Stop a Docker container for a lab instance"""
        if not self.client or not lab_instance.container_id:
            return False
        
        try:
            container = self.client.containers.get(lab_instance.container_id)
            container.stop()
            lab_instance.stop()
            logger.info(f"Container stopped: {lab_instance.container_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop container: {str(e)}")
            return False
    
    def remove_container(self, lab_instance):
        """Remove a Docker container for a lab instance"""
        if not self.client or not lab_instance.container_id:
            return False
        
        try:
            container = self.client.containers.get(lab_instance.container_id)
            container.remove(force=True)
            lab_instance.container_id = None
            lab_instance.access_url = None
            lab_instance.save()
            return True
        except Exception as e:
            logger.error(f"Failed to remove container: {str(e)}")
            return False
            
    def sync_container_status(self, lab_instance):
        """Sync the lab instance status with the actual Docker container status"""
        if not self.client or not lab_instance.container_id:
            return False
        
        try:
            container = self.client.containers.get(lab_instance.container_id)
            
            # Update lab instance status based on container status
            if container.status == 'running':
                lab_instance.status = 'running'
                lab_instance.save()
                return True
            elif container.status == 'exited':
                lab_instance.status = 'stopped'
                lab_instance.save()
                return True
            else:
                # For other statuses, keep as is
                return True
        except Exception as e:
            logger.error(f"Failed to sync container status: {str(e)}")
            return False
            lab_instance.status = 'stopped'
            lab_instance.save()
            logger.info(f"Container removed: {lab_instance.container_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove container: {str(e)}")
            return False
    
    def reset_container(self, lab_instance):
        """Reset a Docker container for a lab instance"""
        if self.remove_container(lab_instance):
            return self.create_container(lab_instance)
        return False

# Create a singleton instance
docker_service = DockerService()