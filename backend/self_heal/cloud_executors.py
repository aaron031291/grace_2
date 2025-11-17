"""
Cloud API Executors - Real cloud infrastructure operations

Integrates with:
- AWS (EC2, Auto Scaling, RDS, S3)
- Docker (local containers)
- Kubernetes (if available)

Gracefully degrades when cloud credentials not available.
"""

import subprocess
from typing import Dict, Any
from datetime import datetime, timezone


class CloudExecutors:
    """
    Cloud infrastructure executors.
    Attempts real cloud operations, falls back gracefully if unavailable.
    """
    
    def __init__(self):
        self.aws_available = self._check_aws()
        self.docker_available = self._check_docker()
        self.kubectl_available = self._check_kubectl()
    
    def _check_aws(self) -> bool:
        """Check if AWS credentials are configured"""
        try:
            import boto3
            # Quick check for credentials
            sts = boto3.client('sts')
            sts.get_caller_identity()
            return True
        except Exception:
            return False
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_kubectl(self) -> bool:
        """Check if kubectl is available"""
        try:
            result = subprocess.run(
                ['kubectl', 'version', '--client'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    # ============= AWS Operations =============
    
    async def aws_scale_instances(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scale AWS Auto Scaling Group"""
        
        if not self.aws_available:
            return {
                "ok": False,
                "error": "AWS credentials not configured",
                "action": "aws_scale_instances",
                "note": "Install boto3 and configure AWS credentials"
            }
        
        asg_name = parameters.get("asg_name")
        desired_capacity = parameters.get("desired_capacity")
        min_delta = parameters.get("min_delta", 1)
        
        try:
            import boto3
            
            client = boto3.client('autoscaling')
            
            # Get current capacity
            response = client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )
            
            if not response['AutoScalingGroups']:
                return {
                    "ok": False,
                    "error": f"Auto Scaling Group not found: {asg_name}",
                    "action": "aws_scale_instances"
                }
            
            asg = response['AutoScalingGroups'][0]
            current_capacity = asg['DesiredCapacity']
            
            # Calculate new capacity
            if desired_capacity is None:
                new_capacity = current_capacity + min_delta
            else:
                new_capacity = desired_capacity
            
            # Apply scaling
            client.update_auto_scaling_group(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=new_capacity
            )
            
            return {
                "ok": True,
                "action": "aws_scale_instances",
                "asg_name": asg_name,
                "old_capacity": current_capacity,
                "new_capacity": new_capacity,
                "delta": new_capacity - current_capacity,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "aws_scale_instances",
                "asg_name": asg_name
            }
    
    async def aws_restart_ec2(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Restart EC2 instance(s)"""
        
        if not self.aws_available:
            return {
                "ok": False,
                "error": "AWS credentials not configured",
                "action": "aws_restart_ec2"
            }
        
        instance_ids = parameters.get("instance_ids", [])
        if isinstance(instance_ids, str):
            instance_ids = [instance_ids]
        
        try:
            import boto3
            
            client = boto3.client('ec2')
            
            # Reboot instances
            client.reboot_instances(InstanceIds=instance_ids)
            
            return {
                "ok": True,
                "action": "aws_restart_ec2",
                "instance_ids": instance_ids,
                "count": len(instance_ids),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "aws_restart_ec2",
                "instance_ids": instance_ids
            }
    
    async def aws_rds_reboot(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reboot RDS database instance"""
        
        if not self.aws_available:
            return {
                "ok": False,
                "error": "AWS credentials not configured",
                "action": "aws_rds_reboot"
            }
        
        db_instance_id = parameters.get("db_instance_id")
        force_failover = parameters.get("force_failover", False)
        
        try:
            import boto3
            
            client = boto3.client('rds')
            
            # Reboot database
            client.reboot_db_instance(
                DBInstanceIdentifier=db_instance_id,
                ForceFailover=force_failover
            )
            
            return {
                "ok": True,
                "action": "aws_rds_reboot",
                "db_instance_id": db_instance_id,
                "force_failover": force_failover,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Reboot initiated, will take 1-2 minutes"
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "aws_rds_reboot",
                "db_instance_id": db_instance_id
            }
    
    # ============= Docker Operations =============
    
    async def docker_restart_container(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Restart Docker container"""
        
        if not self.docker_available:
            return {
                "ok": False,
                "error": "Docker not available",
                "action": "docker_restart_container",
                "note": "Install Docker and ensure daemon is running"
            }
        
        container_name = parameters.get("container_name")
        timeout = parameters.get("timeout", 10)
        
        try:
            # Restart container
            result = subprocess.run(
                ['docker', 'restart', '-t', str(timeout), container_name],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode == 0:
                return {
                    "ok": True,
                    "action": "docker_restart_container",
                    "container_name": container_name,
                    "timeout": timeout,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr,
                    "action": "docker_restart_container",
                    "container_name": container_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": f"Restart timed out after {timeout + 5}s",
                "action": "docker_restart_container",
                "container_name": container_name
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "docker_restart_container",
                "container_name": container_name
            }
    
    async def docker_scale_service(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scale Docker Compose service"""
        
        if not self.docker_available:
            return {
                "ok": False,
                "error": "Docker not available",
                "action": "docker_scale_service"
            }
        
        service_name = parameters.get("service_name")
        replicas = parameters.get("replicas", 1)
        compose_file = parameters.get("compose_file", "docker-compose.yml")
        
        try:
            # Scale service
            result = subprocess.run(
                ['docker-compose', '-f', compose_file, 'up', '-d', '--scale', f'{service_name}={replicas}'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "ok": True,
                    "action": "docker_scale_service",
                    "service_name": service_name,
                    "replicas": replicas,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr,
                    "action": "docker_scale_service",
                    "service_name": service_name
                }
                
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "docker_scale_service",
                "service_name": service_name
            }
    
    # ============= Kubernetes Operations =============
    
    async def k8s_restart_deployment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Restart Kubernetes deployment"""
        
        if not self.kubectl_available:
            return {
                "ok": False,
                "error": "kubectl not available",
                "action": "k8s_restart_deployment",
                "note": "Install kubectl and configure cluster access"
            }
        
        deployment_name = parameters.get("deployment_name")
        namespace = parameters.get("namespace", "default")
        
        try:
            # Rollout restart
            result = subprocess.run(
                ['kubectl', 'rollout', 'restart', 'deployment', deployment_name, '-n', namespace],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "ok": True,
                    "action": "k8s_restart_deployment",
                    "deployment_name": deployment_name,
                    "namespace": namespace,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr,
                    "action": "k8s_restart_deployment",
                    "deployment_name": deployment_name
                }
                
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "k8s_restart_deployment",
                "deployment_name": deployment_name
            }
    
    async def k8s_scale_deployment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scale Kubernetes deployment"""
        
        if not self.kubectl_available:
            return {
                "ok": False,
                "error": "kubectl not available",
                "action": "k8s_scale_deployment"
            }
        
        deployment_name = parameters.get("deployment_name")
        replicas = parameters.get("replicas", 1)
        namespace = parameters.get("namespace", "default")
        
        try:
            # Scale deployment
            result = subprocess.run(
                ['kubectl', 'scale', 'deployment', deployment_name, '--replicas', str(replicas), '-n', namespace],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "ok": True,
                    "action": "k8s_scale_deployment",
                    "deployment_name": deployment_name,
                    "namespace": namespace,
                    "replicas": replicas,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr,
                    "action": "k8s_scale_deployment",
                    "deployment_name": deployment_name
                }
                
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "action": "k8s_scale_deployment",
                "deployment_name": deployment_name
            }
    
    # ============= Health Checks =============
    
    async def get_availability_status(self) -> Dict[str, Any]:
        """Get status of available cloud integrations"""
        return {
            "aws": {
                "available": self.aws_available,
                "services": ["EC2", "Auto Scaling", "RDS"] if self.aws_available else []
            },
            "docker": {
                "available": self.docker_available,
                "services": ["Container Management", "Compose"] if self.docker_available else []
            },
            "kubernetes": {
                "available": self.kubectl_available,
                "services": ["Deployments", "Scaling"] if self.kubectl_available else []
            }
        }


# Singleton instance
cloud_executors = CloudExecutors()
