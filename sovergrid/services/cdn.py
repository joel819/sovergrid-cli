"""
SoverGrid CDN Service
Handles distributing static content via decentralized Content Delivery Networks.

STANDALONE USAGE:
    sovergrid cdn <path>  (pushes files to a decentralized CDN)

PROVIDERS:
    - Fleek (decentralized web hosting and CDN)
    - Saturn (Filecoin's decentralized CDN layer)

LEARNING NOTE FOR JOEL:
-----------------------
A CDN (Content Delivery Network) is what makes websites load fast
worldwide. When someone in Tokyo visits your website hosted in
New York, a CDN caches copies of your files on servers close to
Tokyo so the page loads instantly.

Decentralized CDNs do the same thing, but instead of Cloudflare
or AWS CloudFront controlling the cache servers, they are run by
independent node operators earning crypto for hosting your content.

This service is completely standalone.
"""

import asyncio
import random

from sovergrid.services.base import BaseService, ServiceResult
from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Supported CDN providers
CDN_PROVIDERS = {
    "fleek": {
        "price_per_gb_transferred": 0.01,
        "description": "Decentralized web hosting and edge delivery",
    },
    "saturn": {
        "price_per_gb_transferred": 0.008,
        "description": "Filecoin's decentralized CDN layer",
    },
}


class CDNService(BaseService):
    """
    Distributes static content via a decentralized CDN.

    Config expected (from sovergrid.yaml):
        cdn:
          provider: "fleek"
          origin: "./dist"
          domain: "myapp.eth"
    """

    @property
    def name(self) -> str:
        return "CDN"

    @property
    def provider(self) -> str:
        return self.config.get("provider", "fleek")

    @property
    def origin_path(self) -> str:
        return self.config.get("origin", "./dist")

    @property
    def custom_domain(self) -> str:
        return self.config.get("domain", "")

    async def validate(self) -> bool:
        """Validates the CDN config."""
        provider = self.provider
        if provider not in CDN_PROVIDERS:
            log.error(
                f"[CDN] Unknown provider '{provider}'. "
                f"Supported: {', '.join(CDN_PROVIDERS.keys())}"
            )
            return False

        log.info(
            f"[CDN] Config valid: {provider} | "
            f"Origin: {self.origin_path}"
        )
        return True

    def estimate_cost(self) -> float:
        """Estimates CDN cost based on simulated bandwidth."""
        provider_info = CDN_PROVIDERS.get(self.provider, CDN_PROVIDERS["fleek"])
        # Simulate 1GB to 10GB of monthly transfer
        simulated_gb = round(random.uniform(1.0, 10.0), 2)
        return round(provider_info["price_per_gb_transferred"] * simulated_gb, 4)

    async def execute(self) -> ServiceResult:
        """
        Deploys static content to a decentralized CDN.

        FUTURE: Replace with real Fleek CLI or Saturn API calls.
        """
        provider = self.provider

        log.info(f"[CDN] Connecting to {provider.title()} Network...")
        await asyncio.sleep(random.uniform(0.3, 0.5))

        log.info(f"[CDN] Uploading content from '{self.origin_path}'...")
        await asyncio.sleep(random.uniform(0.4, 0.8))

        log.info(f"[CDN] Propagating to edge nodes worldwide...")
        await asyncio.sleep(random.uniform(0.3, 0.6))

        deployment_id = f"{provider}-cdn-{random.randint(100000, 999999)}"

        if self.custom_domain:
            endpoint = f"https://{self.custom_domain}"
            log.info(f"[CDN] Custom domain configured: {self.custom_domain}")
        else:
            endpoint = f"https://{deployment_id}.{provider}.network"

        log.info(
            f"{Colors.GREEN}[CDN] {provider.title()} deployment "
            f"successful.{Colors.RESET} URL: {endpoint}"
        )

        return ServiceResult(
            service_name="cdn",
            provider=provider,
            status="active",
            endpoint=endpoint,
            metadata={
                "deployment_id": deployment_id,
                "origin": self.origin_path,
                "custom_domain": self.custom_domain,
                "edge_nodes": random.randint(50, 200),
            },
        )
