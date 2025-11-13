"""
End-to-End Test: Book Drop → Ingestion → Self-Healing → Verification
Tests the complete autonomous workflow with failure simulation.
"""

import asyncio
import pytest
import aiohttp
from pathlib import Path
import time
import json


class TestE2ESelfHealingFlow:
    """Test the complete Grace workflow from book upload to self-healing recovery."""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_book_path = "test_data/sample_book.pdf"  # Would need actual test file
        self.session = None

    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()

    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    async def test_complete_workflow(self):
        """Test the full book → ingestion → failure → self-healing → verification flow"""
        await self.setup()

        try:
            # Step 1: Upload book and start ingestion
            ingestion_result = await self._test_book_upload_and_ingestion()
            assert ingestion_result["status"] == "started"

            # Step 2: Monitor ingestion progress
            ingestion_complete = await self._wait_for_ingestion_completion(ingestion_result["task_id"])
            assert ingestion_complete

            # Step 3: Verify initial trust score
            initial_trust = await self._get_trust_score()
            assert initial_trust > 0.8  # Should start high

            # Step 4: Trigger simulated failure
            failure_triggered = await self._trigger_simulated_failure()
            assert failure_triggered

            # Step 5: Verify self-healing activation
            healing_started = await self._wait_for_self_healing_activation()
            assert healing_started

            # Step 6: Monitor self-healing completion
            healing_complete = await self._wait_for_self_healing_completion()
            assert healing_complete

            # Step 7: Verify trust score recovery
            final_trust = await self._get_trust_score()
            assert final_trust >= initial_trust * 0.9  # Allow small dip but recovery

            # Step 8: Test co-pilot interaction
            copilot_response = await self._test_co_pilot_interaction()
            assert len(copilot_response) > 0

            print("✅ Complete E2E workflow test passed!")

        finally:
            await self.teardown()

    async def _test_book_upload_and_ingestion(self):
        """Test book upload and ingestion initiation"""
        # Simulate file upload
        upload_data = aiohttp.FormData()
        upload_data.add_field('file', open(self.test_book_path, 'rb'), filename='sample_book.pdf')

        async with self.session.post(f"{self.base_url}/api/ingestion/upload", data=upload_data) as response:
            result = await response.json()
            return result

    async def _wait_for_ingestion_completion(self, task_id: str, timeout: int = 60):
        """Wait for ingestion to complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            async with self.session.get(f"{self.base_url}/api/ingestion/status/{task_id}") as response:
                status = await response.json()

                if status["status"] == "completed":
                    return True
                elif status["status"] == "failed":
                    return False

            await asyncio.sleep(2)

        return False

    async def _get_trust_score(self):
        """Get current overall trust score"""
        async with self.session.get(f"{self.base_url}/api/self-healing/comprehensive-metrics") as response:
            metrics = await response.json()
            return metrics["trust_levels"]["overall_trust"]

    async def _trigger_simulated_failure(self):
        """Trigger a simulated ingestion failure"""
        failure_payload = {
            "component": "ingestion_pipeline",
            "error_details": {
                "type": "ConnectionError",
                "message": "Simulated database connection failure during ingestion",
                "test_scenario": True
            }
        }

        async with self.session.post(
            f"{self.base_url}/api/self-healing/trigger-manual",
            json=failure_payload
        ) as response:
            result = await response.json()
            return result["status"] == "triggered"

    async def _wait_for_self_healing_activation(self, timeout: int = 30):
        """Wait for self-healing to activate"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            async with self.session.get(f"{self.base_url}/api/self-healing/active-runs") as response:
                active_runs = await response.json()

                if active_runs["count"] > 0:
                    return True

            await asyncio.sleep(1)

        return False

    async def _wait_for_self_healing_completion(self, timeout: int = 60):
        """Wait for self-healing to complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            async with self.session.get(f"{self.base_url}/api/self-healing/active-runs") as response:
                active_runs = await response.json()

                if active_runs["count"] == 0:
                    # Check if there were recent completions
                    async with self.session.get(f"{self.base_url}/api/self-healing/execution-logs?limit=5") as logs_response:
                        logs = await logs_response.json()
                        recent_completions = [log for log in logs["logs"] if log.get("status") == "success"]
                        if recent_completions:
                            return True

            await asyncio.sleep(2)

        return False

    async def _test_co_pilot_interaction(self):
        """Test co-pilot can answer questions about ingested content"""
        copilot_payload = {
            "message": "What is the main theme of the uploaded book?",
            "context": {
                "table_name": "memory_books",
                "action": "query"
            }
        }

        async with self.session.post(
            f"{self.base_url}/api/copilot/chat",
            json=copilot_payload
        ) as response:
            result = await response.json()
            return result.get("response", "")


async def run_e2e_test():
    """Run the complete E2E test"""
    test = TestE2ESelfHealingFlow()
    await test.test_complete_workflow()


if __name__ == "__main__":
    print("🚀 Starting E2E Self-Healing Flow Test...")
    print("This test requires:")
    print("1. Grace system running on localhost:8000")
    print("2. Test book file at test_data/sample_book.pdf")
    print("3. All kernels initialized and active")
    print()

    try:
        asyncio.run(run_e2e_test())
        print("✅ E2E test completed successfully!")
    except Exception as e:
        print(f"❌ E2E test failed: {e}")
        import traceback
        traceback.print_exc()