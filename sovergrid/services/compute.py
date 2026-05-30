"""
SoverGrid Compute Service
Handles deploying containerized apps to decentralized compute networks.

STANDALONE USAGE:
    sovergrid deploy  (uses this service + storage together)

PROVIDERS:
    - Akash Network (primary)
    - Spheron Network (fallback)
    - Golem Network (future)

LEARNING NOTE FOR JOEL:
-----------------------
This file is 100% independent. It does NOT import or depend on
the storage service, the ML service, or any other service.
If you delete every other service file, this one still works perfectly.
That is the entire point of microservices.
"""

import asyncio
import random
from typing import Optional

from sovergrid.services.base import BaseService, ServiceResult
from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Supported compute providers and their simulated price ranges (USD/hour)
COMPUTE_PROVIDERS = {
    "akash": {"min_price": 0.30, "max_price": 0.80, "failure_rate": 0.2},
    "spheron": {"min_price": 0.40, "max_price": 0.90, "failure_rate": 0.05},
    "golem": {"min_price": 0.25, "max_price": 0.70, "failure_rate": 0.1},
}

# Fallback chain: if provider #1 fails, try #2, then #3
FALLBACK_CHAIN = ["akash", "spheron", "golem"]


class ComputeService(BaseService):
    """
    Deploys a containerized application to a decentralized compute provider.

    Config expected (from sovergrid.yaml):
        compute:
          provider: "akash"
          region: "us-west"
          resources:
            cpu: 1
            memory: "512Mi"
    """

    @property
    def name(self) -> str:
        return "Compute"

    @property
    def provider(self) -> str:
        return self.config.get("provider", "akash")

    @property
    def region(self) -> str:
        return self.config.get("region", "auto")

    @property
    def cpu(self) -> int:
        resources = self.config.get("resources", {})
        return resources.get("cpu", 1)

    @property
    def memory(self) -> str:
        resources = self.config.get("resources", {})
        return resources.get("memory", "512Mi")

    async def validate(self) -> bool:
        """Validates the compute config has all required fields."""
        provider = self.provider
        if provider not in COMPUTE_PROVIDERS:
            log.error(
                f"[Compute] Unknown provider '{provider}'. "
                f"Supported: {', '.join(COMPUTE_PROVIDERS.keys())}"
            )
            return False

        if self.cpu < 1:
            log.error("[Compute] CPU must be at least 1 core.")
            return False

        log.info(
            f"[Compute] Config valid: {provider} | "
            f"{self.cpu} CPU | {self.memory} RAM | Region: {self.region}"
        )
        return True

    def estimate_cost(self) -> float:
        """Estimates compute cost based on provider pricing."""
        provider_info = COMPUTE_PROVIDERS.get(self.provider, COMPUTE_PROVIDERS["akash"])
        base_cost = round(
            random.uniform(provider_info["min_price"], provider_info["max_price"]), 4
        )
        # More CPU = more money
        return round(base_cost * self.cpu, 4)

    async def _simulate_provider_call(self, provider: str) -> Optional[dict]:
        """
        Simulates connecting to a compute provider.
        Returns deployment info on success, None on failure.

        FUTURE: Replace with real Akash SDL deployment via akash-py.
        """
        provider_info = COMPUTE_PROVIDERS.get(provider)
        if not provider_info:
            return None

        # Simulate random provider outage
        if random.random() < provider_info["failure_rate"]:
            log.warning(f"[Compute] {provider.title()} Network is unreachable.")
            return None

        log.info(f"[Compute] Connecting to {provider.title()} Network...")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        log.info(f"[Compute] Uploading container image...")
        await asyncio.sleep(random.uniform(0.3, 0.8))

        log.info(f"[Compute] Waiting for deployment confirmation...")
        await asyncio.sleep(random.uniform(0.3, 0.6))

        deploy_id = f"{provider}-{random.randint(100000, 999999)}"
        return {
            "provider": provider,
            "deployment_id": deploy_id,
            "endpoint": f"https://{deploy_id}.{provider}.network",
        }

    async def execute(self) -> ServiceResult:
        """
        Deploys to the configured provider with automatic fallback.
        If the primary provider fails, it walks down the fallback chain.
        """
        # Build fallback chain starting with the user's preferred provider
        chain = [self.provider] + [
            p for p in FALLBACK_CHAIN if p != self.provider
        ]

        for provider in chain:
            result = await self._simulate_provider_call(provider)

            if result is not None:
                log.info(
                    f"{Colors.GREEN}[Compute] {provider.title()} deployment "
                    f"successful.{Colors.RESET} ID: {result['deployment_id']}"
                )
                return ServiceResult(
                    service_name="compute",
                    provider=provider,
                    status="active",
                    endpoint=result["endpoint"],
                    metadata={
                        "deployment_id": result["deployment_id"],
                        "cpu": self.cpu,
                        "memory": self.memory,
                        "region": self.region,
                    },
                )

            # This provider failed, try the next one
            if provider != chain[-1]:
                next_provider = chain[chain.index(provider) + 1]
                log.warning(
                    f"[Compute] Attempting fallback to "
                    f"{next_provider.title()} Network..."
                )

        # All providers failed
        log.error("[Compute] All providers failed. Deployment aborted.")
        return ServiceResult(
            service_name="compute",
            provider="none",
            status="failed",
            metadata={"error": "All providers in fallback chain failed."},
        )
