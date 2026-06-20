"""
SoverGrid Storage Service
Handles pinning files and static assets to decentralized storage networks.

STANDALONE USAGE:
    sovergrid store <path>  (pins files without deploying compute)

PROVIDERS:
    - Filecoin / IPFS (primary)
    - Arweave (permanent storage)

LEARNING NOTE FOR JOEL:
-----------------------
This service is completely independent from compute. A user who
just wants to pin a file to IPFS does NOT need a compute provider,
does NOT need a Dockerfile, and does NOT need a CPU config.
They just point at a file and this service handles the rest.
"""

import asyncio
import random
from typing import Optional

from sovergrid.services.base import BaseService, ServiceResult
from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Supported storage providers
STORAGE_PROVIDERS = {
    "filecoin": {
        "price_per_gb": 0.02,
        "gateway": "https://ipfs.io/ipfs",
    },
    "arweave": {
        "price_per_gb": 0.05,
        "gateway": "https://arweave.net",
    },
    "ipfs": {
        "price_per_gb": 0.01,
        "gateway": "https://dweb.link/ipfs",
    },
}


class StorageService(BaseService):
    """
    Pins files or directories to decentralized storage.

    Config expected (from sovergrid.yaml):
        storage:
          provider: "filecoin"
          pin: true
    """

    @property
    def name(self) -> str:
        return "Storage"

    @property
    def provider(self) -> str:
        return self.config.get("provider", "filecoin")

    @property
    def should_pin(self) -> bool:
        return self.config.get("pin", True)

    async def validate(self) -> bool:
        """Validates the storage config."""
        provider = self.provider
        if provider not in STORAGE_PROVIDERS:
            log.error(
                f"[Storage] Unknown provider '{provider}'. "
                f"Supported: {', '.join(STORAGE_PROVIDERS.keys())}"
            )
            return False

        log.info(f"[Storage] Config valid: {provider} | Pin: {self.should_pin}")
        return True

    def estimate_cost(self) -> float:
        """
        Estimates storage cost.
        In the future, this will calculate based on actual file size.
        For now, simulate a small deployment (~50MB).
        """
        provider_info = STORAGE_PROVIDERS.get(
            self.provider, STORAGE_PROVIDERS["filecoin"]
        )
        # Simulate 50MB to 500MB of data
        simulated_gb = round(random.uniform(0.05, 0.5), 4)
        return round(provider_info["price_per_gb"] * simulated_gb, 4)

    async def execute(self) -> ServiceResult:
        """
        Pins assets to the configured storage provider.

        FUTURE: Replace with real Filecoin/IPFS pinning via web3.storage
        or nft.storage API calls.
        """
        provider = self.provider
        provider_info = STORAGE_PROVIDERS[provider]

        log.info(f"[Storage] Connecting to {provider.title()}...")
        await asyncio.sleep(random.uniform(0.3, 0.6))

        log.info(f"[Storage] Uploading and pinning assets...")
        await asyncio.sleep(random.uniform(0.5, 1.2))

        # Generate the Content Identifier (CID)
        if provider == "arweave":
            generated_id = f"ar-{random.randint(10**10, 10**11 - 1)}"
            gateway_url = f"{provider_info['gateway']}/{generated_id}"
        else:
            generated_cid = f"Qm{random.randint(10**44, 10**45 - 1)}"
            generated_id = generated_cid
            gateway_url = f"{provider_info['gateway']}/{generated_cid}"

        log.info(
            f"{Colors.GREEN}[Storage] {provider.title()} pinning "
            f"successful.{Colors.RESET} CID: {generated_id[:20]}..."
        )

        return ServiceResult(
            service_name="storage",
            provider=provider,
            status="pinned",
            endpoint=gateway_url,
            metadata={
                "cid": generated_id,
                "pinned": self.should_pin,
            },
        )
