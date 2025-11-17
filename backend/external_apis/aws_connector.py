"""AWS SDK Integration with Governance and Security

Integrates with AWS using boto3 with S3, Lambda, EC2 operations.
All operations governed and verified with cost tracking.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    boto3 = None
    ClientError = Exception
    BotoCoreError = Exception

from ..secrets_vault import secrets_vault
from ..governance import GovernanceEngine
from ..hunter import Hunter
from ..verification import VerificationEngine
from ..memory_service import MemoryService
from ..immutable_log import ImmutableLogger


class AWSClient:
    """AWS client with governance and security"""
    
    def __init__(self, actor: str = "grace"):
        """
        Initialize AWS client
        
        Args:
            actor: User/service making AWS operations
        """
        if boto3 is None:
            raise ImportError("boto3 not installed. Run: pip install boto3")
        
        self.actor = actor
        self.s3_client = None
        self.lambda_client = None
        self.ec2_client = None
        self.governance = GovernanceEngine()
        self.hunter = Hunter()
        self.verification = VerificationEngine()
        self.memory = MemoryService()
        self.audit = ImmutableLogger()
        
        # Cost tracking
        self.cost_tracker = {}
    
    async def authenticate_with_credentials(
        self,
        access_key_id_key: str = "aws_access_key_id",
        secret_access_key_key: str = "aws_secret_access_key",
        region_name: str = "us-east-1"
    ) -> bool:
        """
        Authenticate using credentials from secrets vault
        
        Args:
            access_key_id_key: Vault key for AWS access key ID
            secret_access_key_key: Vault key for AWS secret access key
            region_name: AWS region
        
        Returns:
            True if authentication successful
        """
        try:
            # Retrieve credentials from vault
            access_key_id = await secrets_vault.retrieve_secret(
                secret_key=access_key_id_key,
                accessor=self.actor,
                service="aws"
            )
            
            secret_access_key = await secrets_vault.retrieve_secret(
                secret_key=secret_access_key_key,
                accessor=self.actor,
                service="aws"
            )
            
            # Create AWS clients
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )
            
            self.lambda_client = boto3.client(
                'lambda',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )
            
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )
            
            # Test authentication with S3
            self.s3_client.list_buckets()
            
            # Log authentication
            await self.audit.log_event(
                actor=self.actor,
                action="aws_auth",
                resource="aws",
                result="success",
                details={"region": region_name}
            )
            
            print(f"✓ AWS authenticated in region {region_name}")
            return True
            
        except Exception as e:
            await self.audit.log_event(
                actor=self.actor,
                action="aws_auth",
                resource="aws",
                result="failure",
                details={"error": str(e)}
            )
            raise PermissionError(f"AWS authentication failed: {e}")
    
    async def _check_governance(
        self,
        action: str,
        resource: str,
        payload: Dict[str, Any]
    ) -> None:
        """Check governance policy before action"""
        
        result = await self.governance.check(
            actor=self.actor,
            action=f"aws_{action}",
            resource=resource,
            payload=payload
        )
        
        if result["decision"] == "deny":
            raise PermissionError(f"Governance denied: {result.get('reason', 'No reason')}")
        
        if result["decision"] == "parliament_pending":
            raise PermissionError(
                f"Parliament review required. Session ID: {result.get('parliament_session_id')}"
            )
    
    async def _create_verification(
        self,
        action: str,
        resource: str,
        input_data: Dict[str, Any]
    ) -> int:
        """Create verification envelope"""
        
        action_id = f"aws_{action}_{datetime.utcnow().timestamp()}"
        
        return await self.verification.log_verified_action(
            action_id=action_id,
            actor=self.actor,
            action_type=f"aws_{action}",
            resource=resource,
            input_data=input_data
        )
    
    async def _track_cost(
        self,
        service: str,
        operation: str,
        estimated_cost: float = 0.0
    ):
        """Track AWS operation costs"""
        
        key = f"{service}_{operation}"
        if key not in self.cost_tracker:
            self.cost_tracker[key] = {"count": 0, "total_cost": 0.0}
        
        self.cost_tracker[key]["count"] += 1
        self.cost_tracker[key]["total_cost"] += estimated_cost
        
        # Store in memory for cost analysis
        await self.memory.store_memory(
            agent=self.actor,
            memory_type="aws_cost",
            content=json.dumps(self.cost_tracker, indent=2),
            metadata={"service": service, "operation": operation, "cost": estimated_cost}
        )
    
    # ==================== S3 Operations ====================
    
    async def s3_upload_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3 (requires governance)
        
        Args:
            bucket: S3 bucket name
            key: Object key
            file_path: Local file path
            metadata: Optional metadata
        
        Returns:
            Upload information
        """
        if not self.s3_client:
            raise RuntimeError("Not authenticated. Call authenticate_with_credentials() first")
        
        # Governance check
        await self._check_governance(
            action="s3_upload",
            resource=f"s3://{bucket}/{key}",
            payload={"bucket": bucket, "key": key, "file_path": file_path}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="s3_upload",
            resource=f"s3://{bucket}/{key}",
            input_data={"bucket": bucket, "key": key, "file_path": file_path}
        )
        
        try:
            # Upload file
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
            
            # Get file size for cost tracking
            file_size = os.path.getsize(file_path)
            estimated_cost = file_size / (1024 ** 3) * 0.023  # Rough estimate: $0.023 per GB
            
            await self._track_cost("s3", "upload", estimated_cost)
            
            result = {
                "bucket": bucket,
                "key": key,
                "size": file_size,
                "verification_id": verification_id,
                "estimated_cost": estimated_cost
            }
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_upload",
                resource=f"s3://{bucket}/{key}",
                result="success",
                details={"size": file_size, "key": key}
            )
            
            return result
            
        except (ClientError, BotoCoreError) as e:
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_upload",
                resource=f"s3://{bucket}/{key}",
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def s3_download_file(
        self,
        bucket: str,
        key: str,
        dest_path: str
    ) -> Dict[str, Any]:
        """
        Download file from S3
        
        Args:
            bucket: S3 bucket name
            key: Object key
            dest_path: Local destination path
        
        Returns:
            Download information
        """
        if not self.s3_client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="s3_download",
            resource=f"s3://{bucket}/{key}",
            payload={"bucket": bucket, "key": key, "dest_path": dest_path}
        )
        
        try:
            # Download file
            self.s3_client.download_file(bucket, key, dest_path)
            
            # Get file size
            file_size = os.path.getsize(dest_path)
            
            # Hunter scan downloaded file
            await self.hunter.inspect(
                actor=self.actor,
                action="aws_s3_downloaded_file",
                resource=dest_path,
                payload={"bucket": bucket, "key": key, "size": file_size}
            )
            
            await self._track_cost("s3", "download", 0.0)  # Downloads are free
            
            result = {
                "bucket": bucket,
                "key": key,
                "dest_path": dest_path,
                "size": file_size
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_download",
                resource=f"s3://{bucket}/{key}",
                result="success",
                details={"size": file_size}
            )
            
            return result
            
        except (ClientError, BotoCoreError) as e:
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_download",
                resource=f"s3://{bucket}/{key}",
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def s3_list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List objects in S3 bucket
        
        Args:
            bucket: S3 bucket name
            prefix: Object prefix filter
            max_keys: Maximum objects to return
        
        Returns:
            List of objects
        """
        if not self.s3_client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="s3_list",
            resource=f"s3://{bucket}",
            payload={"bucket": bucket, "prefix": prefix}
        )
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                    "etag": obj["ETag"]
                })
            
            await self._track_cost("s3", "list", 0.005)  # $0.005 per 1000 requests
            
            # Store in memory
            await self.memory.store_memory(
                agent=self.actor,
                memory_type="aws_s3_list",
                content=json.dumps(objects, indent=2),
                metadata={"bucket": bucket, "prefix": prefix, "count": len(objects)}
            )
            
            return objects
            
        except (ClientError, BotoCoreError) as e:
            raise
    
    async def s3_delete_object(
        self,
        bucket: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Delete object from S3 (requires governance)
        
        Args:
            bucket: S3 bucket name
            key: Object key
        
        Returns:
            Deletion confirmation
        """
        if not self.s3_client:
            raise RuntimeError("Not authenticated")
        
        # Governance (deletion is sensitive)
        await self._check_governance(
            action="s3_delete",
            resource=f"s3://{bucket}/{key}",
            payload={"bucket": bucket, "key": key}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="s3_delete",
            resource=f"s3://{bucket}/{key}",
            input_data={"bucket": bucket, "key": key}
        )
        
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            
            result = {
                "bucket": bucket,
                "key": key,
                "status": "deleted",
                "verification_id": verification_id
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_delete",
                resource=f"s3://{bucket}/{key}",
                result="success",
                details={"key": key}
            )
            
            return result
            
        except (ClientError, BotoCoreError) as e:
            await self.audit.log_event(
                actor=self.actor,
                action="aws_s3_delete",
                resource=f"s3://{bucket}/{key}",
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    # ==================== Lambda Operations ====================
    
    async def lambda_invoke_function(
        self,
        function_name: str,
        payload: Dict[str, Any],
        invocation_type: str = "RequestResponse"
    ) -> Dict[str, Any]:
        """
        Invoke AWS Lambda function (requires governance)
        
        Args:
            function_name: Lambda function name
            payload: Function payload
            invocation_type: RequestResponse, Event, or DryRun
        
        Returns:
            Invocation result
        """
        if not self.lambda_client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="lambda_invoke",
            resource=function_name,
            payload={"function_name": function_name, "payload": payload}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="lambda_invoke",
            resource=function_name,
            input_data={"function_name": function_name, "payload": payload}
        )
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload)
            )
            
            response_payload = json.load(response['Payload'])
            
            result = {
                "function_name": function_name,
                "status_code": response['StatusCode'],
                "payload": response_payload,
                "verification_id": verification_id
            }
            
            # Cost tracking (rough estimate)
            await self._track_cost("lambda", "invoke", 0.0000002)  # $0.20 per 1M requests
            
            await self.audit.log_event(
                actor=self.actor,
                action="aws_lambda_invoke",
                resource=function_name,
                result="success",
                details={"status_code": response['StatusCode']}
            )
            
            return result
            
        except (ClientError, BotoCoreError) as e:
            await self.audit.log_event(
                actor=self.actor,
                action="aws_lambda_invoke",
                resource=function_name,
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def lambda_list_functions(self, max_items: int = 50) -> List[Dict[str, Any]]:
        """List Lambda functions"""
        
        if not self.lambda_client:
            raise RuntimeError("Not authenticated")
        
        await self._check_governance(
            action="lambda_list",
            resource="lambda",
            payload={"max_items": max_items}
        )
        
        try:
            response = self.lambda_client.list_functions(MaxItems=max_items)
            
            functions = []
            for func in response.get('Functions', []):
                functions.append({
                    "name": func["FunctionName"],
                    "runtime": func["Runtime"],
                    "handler": func["Handler"],
                    "code_size": func["CodeSize"],
                    "memory_size": func["MemorySize"],
                    "timeout": func["Timeout"],
                    "last_modified": func["LastModified"]
                })
            
            return functions
            
        except (ClientError, BotoCoreError) as e:
            raise
    
    # ==================== EC2 Operations (Read-only for safety) ====================
    
    async def ec2_list_instances(self) -> List[Dict[str, Any]]:
        """List EC2 instances (read-only)"""
        
        if not self.ec2_client:
            raise RuntimeError("Not authenticated")
        
        await self._check_governance(
            action="ec2_list",
            resource="ec2",
            payload={}
        )
        
        try:
            response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        "instance_id": instance["InstanceId"],
                        "instance_type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "launch_time": instance["LaunchTime"].isoformat(),
                        "private_ip": instance.get("PrivateIpAddress"),
                        "public_ip": instance.get("PublicIpAddress"),
                        "tags": {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                    })
            
            # Store in memory
            await self.memory.store_memory(
                agent=self.actor,
                memory_type="aws_ec2_list",
                content=json.dumps(instances, indent=2),
                metadata={"count": len(instances)}
            )
            
            return instances
            
        except (ClientError, BotoCoreError) as e:
            raise
    
    async def ec2_get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get EC2 instance status (read-only)"""
        
        if not self.ec2_client:
            raise RuntimeError("Not authenticated")
        
        try:
            response = self.ec2_client.describe_instance_status(InstanceIds=[instance_id])
            
            if not response['InstanceStatuses']:
                return {"instance_id": instance_id, "status": "not_found"}
            
            status = response['InstanceStatuses'][0]
            
            return {
                "instance_id": instance_id,
                "instance_state": status["InstanceState"]["Name"],
                "system_status": status["SystemStatus"]["Status"],
                "instance_status": status["InstanceStatus"]["Status"]
            }
            
        except (ClientError, BotoCoreError) as e:
            raise
    
    async def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        
        return {
            "tracker": self.cost_tracker,
            "total_estimated_cost": sum(v["total_cost"] for v in self.cost_tracker.values()),
            "total_operations": sum(v["count"] for v in self.cost_tracker.values())
        }
