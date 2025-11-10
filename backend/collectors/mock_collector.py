"""Mock metrics collector for agentic systems testing"""

import asyncio
import random
from datetime import datetime
from backend.trigger_mesh import trigger_mesh, TriggerEvent


class MockMetricsCollector:
    """Generates realistic mock metrics for testing agentic systems"""

    def __init__(self):
        self.running = False
        self.task = None

    async def start(self):
        """Start collecting mock metrics"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._collect_metrics())
            print("✅ Mock metrics collector started")

    async def stop(self):
        """Stop collecting metrics"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("✅ Mock metrics collector stopped")

    async def _collect_metrics(self):
        """Main metrics collection loop"""
        try:
            while self.running:
                await self._publish_api_metrics()
                await self._publish_infrastructure_metrics()
                await self._publish_business_metrics()

                # Collect every 30 seconds
                await asyncio.sleep(30)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"✗ Mock collector error: {e}")

    async def _publish_api_metrics(self):
        """Publish API performance metrics"""
        metrics = [
            ("api_latency_p95", random.gauss(200, 50), "ms"),
            ("api_error_rate", random.uniform(0.001, 0.05), "ratio"),
            ("api_request_rate", random.gauss(150, 30), "req_per_sec"),
            ("api_success_rate", random.uniform(0.95, 0.999), "ratio"),
        ]

        for metric_name, value, unit in metrics:
            # Ensure reasonable bounds
            if "rate" in metric_name and "error" not in metric_name:
                value = max(0, min(value, 1000))
            elif "latency" in metric_name:
                value = max(10, min(value, 2000))
            elif "error_rate" in metric_name:
                value = max(0, min(value, 0.1))
            elif "success_rate" in metric_name:
                value = max(0.8, min(value, 1.0))

            await trigger_mesh.publish(TriggerEvent(
                event_type=f"metrics.{metric_name}",
                source="mock_collector",
                actor="mock_metrics",
                resource="api-service",
                payload={
                    "value": round(value, 3),
                    "unit": unit,
                    "metric": metric_name,
                    "service": "api-gateway",
                    "environment": "production"
                }
            ))

    async def _publish_infrastructure_metrics(self):
        """Publish infrastructure metrics"""
        metrics = [
            ("cpu_utilization", random.gauss(65, 15), "percent"),
            ("memory_utilization", random.gauss(70, 20), "percent"),
            ("disk_utilization", random.gauss(45, 10), "percent"),
            ("network_in", random.gauss(50, 20), "Mbps"),
            ("network_out", random.gauss(30, 15), "Mbps"),
        ]

        for metric_name, value, unit in metrics:
            # Ensure reasonable bounds
            if "utilization" in metric_name:
                value = max(0, min(value, 100))
            elif "network" in metric_name:
                value = max(0, min(value, 200))

            await trigger_mesh.publish(TriggerEvent(
                event_type=f"metrics.{metric_name}",
                source="mock_collector",
                actor="mock_metrics",
                resource="web-server-01",
                payload={
                    "value": round(value, 2),
                    "unit": unit,
                    "metric": metric_name,
                    "host": "web-server-01",
                    "datacenter": "us-east-1"
                }
            ))

    async def _publish_business_metrics(self):
        """Publish business/application metrics"""
        metrics = [
            ("user_sessions_active", random.gauss(1200, 150), "count"),  # Keep high
            ("orders_per_minute", random.gauss(30, 5), "count"),  # Keep above 50 for good status
            ("payment_success_rate", random.uniform(0.98, 0.999), "ratio"),  # Keep high
            ("checkout_conversion", random.uniform(0.03, 0.08), "ratio"),  # Keep above 0.02
        ]

        for metric_name, value, unit in metrics:
            # Ensure reasonable bounds within good ranges
            if "rate" in metric_name or "conversion" in metric_name:
                value = max(0.02, min(value, 1.0))  # Keep above 0.02 for good status
            elif "sessions" in metric_name or "orders" in metric_name:
                value = max(50, int(value))  # Keep above 50 for good status

            await trigger_mesh.publish(TriggerEvent(
                event_type=f"metrics.{metric_name}",
                source="mock_collector",
                actor="mock_metrics",
                resource="ecommerce-app",
                payload={
                    "value": round(value, 3) if isinstance(value, float) else value,
                    "unit": unit,
                    "metric": metric_name,
                    "application": "ecommerce-platform",
                    "business_unit": "retail"
                }
            ))


# Global instance
mock_collector = MockMetricsCollector()