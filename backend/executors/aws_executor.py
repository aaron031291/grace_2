"""AWS cloud executor for real infrastructure actions"""

import asyncio
from typing import Dict, Any
from datetime import datetime
from backend.trigger_mesh import trigger_mesh, TriggerEvent


class AWSExecutor:
    """Executes real AWS infrastructure actions"""

    def __init__(self):
        self.client = None
        self.initialized = False

    async def initialize(self):
        """Initialize AWS client"""
        try:
            import boto3
            # Use default credentials from environment or IAM roles
            self.client = boto3.client('autoscaling')
            self.initialized = True
            print("✅ AWS Executor initialized")
        except ImportError:
            print("⚠️ AWS Executor: boto3 not installed - install with: pip install boto3")
        except Exception as e:
            print(f"⚠️ AWS Executor initialization failed: {e}")

    async def execute_scale_action(self, node_id: str, target_capacity: int, **kwargs) -> Dict[str, Any]:
        """Execute real AWS Auto Scaling Group scaling"""
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                return {"error": "AWS client not initialized", "mock": True}

        try:
            # Real AWS API call
            response = self.client.update_auto_scaling_group(
                AutoScalingGroupName=node_id,
                DesiredCapacity=int(target_capacity),
                HonorCooldown=False  # Immediate scaling for emergencies
            )

            # Wait for scaling to complete
            waiter = self.client.get_waiter('group_in_service')
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: waiter.wait(
                    AutoScalingGroupNames=[node_id],
                    WaiterConfig={'Delay': 15, 'MaxAttempts': 20}
                )
            )

            # Publish success event
            await trigger_mesh.publish(TriggerEvent(
                event_type="infrastructure.scaled",
                source="aws_executor",
                actor="grace_agentic",
                resource=node_id,
                payload={
                    "action": "scale_up" if target_capacity > kwargs.get('current_capacity', 0) else "scale_down",
                    "target_capacity": target_capacity,
                    "previous_capacity": kwargs.get('current_capacity'),
                    "aws_response": response
                }
            ))

            return {
                "success": True,
                "scaled": True,
                "new_capacity": target_capacity,
                "aws_response": response,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            # Publish failure event
            await trigger_mesh.publish(TriggerEvent(
                event_type="infrastructure.scale_failed",
                source="aws_executor",
                actor="grace_agentic",
                resource=node_id,
                payload={
                    "error": str(e),
                    "target_capacity": target_capacity,
                    "action": "scale_failed"
                }
            ))

            return {
                "success": False,
                "error": str(e),
                "target_capacity": target_capacity,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def execute_restart_action(self, instance_id: str, **kwargs) -> Dict[str, Any]:
        """Execute real AWS EC2 instance restart"""
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                return {"error": "AWS client not initialized", "mock": True}

        try:
            # Switch to EC2 client for instance operations
            import boto3
            ec2_client = boto3.client('ec2')

            # Real AWS API call to restart instance
            response = ec2_client.reboot_instances(InstanceIds=[instance_id])

            # Publish success event
            await trigger_mesh.publish(TriggerEvent(
                event_type="infrastructure.restarted",
                source="aws_executor",
                actor="grace_agentic",
                resource=instance_id,
                payload={
                    "action": "restart",
                    "instance_id": instance_id,
                    "aws_response": response
                }
            ))

            return {
                "success": True,
                "restarted": True,
                "instance_id": instance_id,
                "aws_response": response,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            # Publish failure event
            await trigger_mesh.publish(TriggerEvent(
                event_type="infrastructure.restart_failed",
                source="aws_executor",
                actor="grace_agentic",
                resource=instance_id,
                payload={
                    "error": str(e),
                    "instance_id": instance_id,
                    "action": "restart_failed"
                }
            ))

            return {
                "success": False,
                "error": str(e),
                "instance_id": instance_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_asg_status(self, asg_name: str) -> Dict[str, Any]:
        """Get current Auto Scaling Group status"""
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                return {"error": "AWS client not initialized"}

        try:
            response = self.client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )

            if response['AutoScalingGroups']:
                asg = response['AutoScalingGroups'][0]
                return {
                    "name": asg['AutoScalingGroupName'],
                    "current_capacity": asg['DesiredCapacity'],
                    "min_size": asg['MinSize'],
                    "max_size": asg['MaxSize'],
                    "instances": len(asg['Instances']),
                    "status": "healthy"
                }
            else:
                return {"error": f"Auto Scaling Group {asg_name} not found"}

        except Exception as e:
            return {"error": str(e)}


# Global instance
aws_executor = AWSExecutor()
