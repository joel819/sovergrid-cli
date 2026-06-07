"""
SoverGrid Orchestrator
Routes deployment requests through the SoverGrid Backend API.
Handles compute and storage deployments concurrently with cost protection.
"""

import asyncio
import json
import random
import time
import httpx
import os
from dataclasses import dataclass
from pathlib import Path

from sovergrid.config import SoverGridConfig
from sovergrid.logger import get_logger, Colors
from sovergrid.services.compute import COMPUTE_PROVIDERS

log = get_logger(__name__)

CREDENTIALS_DIR = Path.home() / ".sovergrid"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"


def _load_auth_headers() -> dict:
    """Load JWT from ~/.sovergrid/credentials.json and return as Authorization header."""
    if not CREDENTIALS_FILE.exists():
        log.error(
            f"{Colors.RED}Not authenticated.{Colors.RESET}\n"
            f"  Run {Colors.CYAN}sovergrid login{Colors.RESET} or "
            f"{Colors.CYAN}sovergrid register{Colors.RESET} first."
        )
        raise SystemExit(1)

    with open(CREDENTIALS_FILE, "r") as f:
        creds = json.load(f)

    token = creds.get("access_token")
    if not token:
        log.error("Credentials file is missing the access token. Run 'sovergrid login' again.")
        raise SystemExit(1)

    return {"Authorization": f"Bearer {token}"}


@dataclass
class CostBreakdown:
    """
    Represents the fee split for a single deployment.
    Maps directly to the tokenomics in SoverGrid_Payment_Routing.md:
      60% -> Compute Provider (Akash/Spheron)
      20% -> SoverGrid Treasury
      15% -> SVR Stakers
       5% -> Auto-Liquidity Pool
    """
    base_cost: float          # What the compute provider charges
    treasury_fee: float       # 20% to SoverGrid Foundation
    staker_reward: float      # 15% to SVR token stakers
    liquidity_fee: float      # 5% auto-routed to Uniswap pool
    total: float              # What the developer actually pays

    def display(self) -> str:
        return (
            f"\n"
            f"  {Colors.DIM}{'=' * 40}{Colors.RESET}\n"
            f"  {Colors.BOLD}Cost Breakdown{Colors.RESET}\n"
            f"  {Colors.DIM}{'=' * 40}{Colors.RESET}\n"
            f"  Compute ({self.provider}):    ${self.base_cost:.4f}\n"
            f"  Treasury (20%):        ${self.treasury_fee:.4f}\n"
            f"  Staker Rewards (15%):  ${self.staker_reward:.4f}\n"
            f"  Auto-Liquidity (5%):   ${self.liquidity_fee:.4f}\n"
            f"  {Colors.DIM}{'-' * 40}{Colors.RESET}\n"
            f"  {Colors.BOLD}{Colors.GREEN}Total:                  "
            f"${self.total:.4f}{Colors.RESET}\n"
        )

    provider: str = "akash"


def calculate_cost(base_cost: float, provider: str = "akash") -> CostBreakdown:
    """
    Calculates the full fee split from a base compute cost.
    The base cost is what the decentralized network charges.
    SoverGrid adds its fees on top.

    In the real implementation, base_cost will come from pinging
    the Akash/Spheron marketplace API for live pricing.
    """
    treasury_fee = base_cost * 0.20
    staker_reward = base_cost * 0.15
    liquidity_fee = base_cost * 0.05
    total = base_cost + treasury_fee + staker_reward + liquidity_fee

    return CostBreakdown(
        base_cost=base_cost,
        treasury_fee=treasury_fee,
        staker_reward=staker_reward,
        liquidity_fee=liquidity_fee,
        total=total,
        provider=provider,
    )


async def _simulate_api_call(provider: str, action: str, duration: float):
    """
    Simulates an async API call with realistic timing.
    In the real implementation, this will be an actual HTTP request
    to the Akash or Filecoin API.
    """
    log.info(f"Connecting to {provider}...")
    await asyncio.sleep(duration * 0.3)

    log.info(f"Uploading container image to {provider}...")
    await asyncio.sleep(duration * 0.4)

    log.info(f"Waiting for {provider} to confirm {action}...")
    await asyncio.sleep(duration * 0.3)


async def deploy_compute(config: SoverGridConfig, provider: str) -> dict:
    """
    Simulates deploying a containerized app to a compute network by routing
    the request through the local FastAPI backend.
    """
    log.info(
        f"Deploying '{config.app_name}' to {provider.title()} Network "
        f"via SoverGrid Backend..."
    )

    auth_headers = _load_auth_headers()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "app_name": config.app_name,
                "provider": provider.lower(),
                "config": {
                    "cpu": config.cpu,
                    "memory": config.memory
                }
            }
            api_url = os.environ.get("SOVERGRID_API_URL", "https://web-production-4966c.up.railway.app")
            response = await client.post(f"{api_url}/deploy", json=payload, headers=auth_headers)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("data", {})
            deploy_url = result_data.get("url", f"https://{config.app_name}.{provider}.network")
            
            log.info(f"{Colors.GREEN}{provider.title()} deployment successful.{Colors.RESET}")
            
            return {
                "provider": provider,
                "deployment_id": "backend-managed",
                "status": "active",
                "endpoint": deploy_url,
                "cpu": config.cpu,
                "memory": config.memory,
            }
    except Exception as e:
        log.error(f"Backend deployment failed: {str(e)}")
        raise


async def deploy_to_filecoin(config: SoverGridConfig) -> dict:
    """
    Simulates pinning static assets to Filecoin/IPFS by routing
    the request through the local FastAPI backend.
    """
    if config.storage_provider != "filecoin":
        log.debug("Skipping Filecoin (storage provider is not filecoin).")
        return None

    log.info("Pinning static assets to Filecoin/IPFS via SoverGrid Backend...")

    auth_headers = _load_auth_headers()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "app_name": config.app_name,
                "provider": "filecoin",
                "config": {"pin": True}
            }
            api_url = os.environ.get("SOVERGRID_API_URL", "https://web-production-4966c.up.railway.app")
            response = await client.post(f"{api_url}/deploy", json=payload, headers=auth_headers)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("data", {})
            gateway_url = result_data.get("url", "ipfs://unknown")
            
            log.info(f"{Colors.GREEN}Filecoin pinning successful.{Colors.RESET}")
            
            return {
                "provider": "filecoin",
                "cid": gateway_url.split("/")[-1],
                "status": "pinned",
                "gateway_url": gateway_url,
            }
    except Exception as e:
        log.error(f"Backend storage deployment failed: {str(e)}")
        raise


async def run_deployment(config: SoverGridConfig) -> dict:
    """
    Orchestrates a full mock deployment with Fallbacks & Cost Protection.
    """
    log.info(f"Starting deployment pipeline for '{config.app_name}'...")
    log.info(f"Config summary:{config.summary()}")

    start_time = time.time()

    active_provider = config.compute_provider

    if getattr(config, 'green', False):
        green_providers = [
            p for p, data in COMPUTE_PROVIDERS.items() 
            if data.get("green_certified", False)
        ]
        
        if not green_providers:
            log.error("No green-certified providers available. Remove green: true to use all providers.")
            return None
            
        if active_provider not in green_providers:
            log.warning(f"Preferred provider '{active_provider}' is not green-certified.")
            active_provider = green_providers[0]
            log.warning(f"Auto-switching to green provider: '{active_provider}'")

    base_compute_cost = round(random.uniform(0.30, 0.80), 4)
    cost = calculate_cost(base_compute_cost, provider=active_provider)

    # 1. Cost Protection Check
    if cost.total > config.max_budget:
        log.error(f"Deployment canceled! Provider cost (${cost.total:.4f}) exceeds your max_budget (${config.max_budget:.4f}).")
        return None

    # 2. Simulate Provider Outage & Fallback
    # 20% chance Akash fails so we can test the Spheron fallback
    if active_provider == "akash" and random.random() < 0.2:
        log.error("Akash Network is currently unreachable or bidding failed.")
        log.warning("Attempting automatic fallback to Spheron Network...")
        
        fallback_base_cost = round(random.uniform(0.40, 0.90), 4)
        fallback_cost = calculate_cost(fallback_base_cost, provider="spheron")
        
        # Protect against expensive fallbacks!
        if fallback_cost.total > config.max_budget:
            log.error(f"Fallback to Spheron canceled. Cost (${fallback_cost.total:.4f}) exceeds your max_budget (${config.max_budget:.4f}).")
            log.error("Please increase your max_budget in sovergrid.yaml or try again later.")
            return None
            
        log.info(f"{Colors.GREEN}Fallback approved. Spheron is within budget.${Colors.RESET}")
        active_provider = "spheron"
        cost = fallback_cost

    # 3. Run compute and storage deployments concurrently
    compute_task = deploy_compute(config, provider=active_provider)
    storage_task = deploy_to_filecoin(config)
    
    compute_result, filecoin_result = await asyncio.gather(compute_task, storage_task)

    elapsed = round(time.time() - start_time, 2)

    log.info(
        f"\n"
        f"  {Colors.BOLD}{Colors.GREEN}"
        f"  Deployment Complete{Colors.RESET}\n"
        f"  Time: {elapsed}s\n"
        f"  Endpoint: {compute_result['endpoint']}\n"
        f"{cost.display()}"
    )

    return {
        "app_name": config.app_name,
        "compute": compute_result,
        "storage": filecoin_result,
        "cost": {
            "base": cost.base_cost,
            "total": cost.total,
            "currency": config.payment_token,
        },
        "elapsed_seconds": elapsed,
    }
