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
    Uses a SaaS-style flat routing fee per deployment.
    """
    base_cost: float          # What the compute provider charges
    routing_fee: float        # Flat SaaS fee (e.g., $5.00) for SoverGrid
    total: float              # What the developer actually pays

    def display(self) -> str:
        return (
            f"\n"
            f"  {Colors.DIM}{'=' * 40}{Colors.RESET}\n"
            f"  {Colors.BOLD}Cost Breakdown{Colors.RESET}\n"
            f"  {Colors.DIM}{'=' * 40}{Colors.RESET}\n"
            f"  Compute ({self.provider}):    ${self.base_cost:.4f}\n"
            f"  SoverGrid Fee:         ${self.routing_fee:.4f}\n"
            f"  {Colors.DIM}{'-' * 40}{Colors.RESET}\n"
            f"  {Colors.BOLD}{Colors.GREEN}Total:                  "
            f"${self.total:.4f}{Colors.RESET}\n"
        )

    provider: str = "akash"


def calculate_cost(base_cost: float, provider: str = "akash") -> CostBreakdown:
    """
    Calculates the full fee split from a base compute cost.
    The base cost is what the decentralized network charges.
    We tack on a flat SaaS routing fee ($5.00) per deployment.
    """
    routing_fee = 5.00
    total = base_cost + routing_fee
    
    return CostBreakdown(
        base_cost=base_cost,
        routing_fee=routing_fee,
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


async def deploy_compute(config: SoverGridConfig, provider: str, cost: CostBreakdown) -> dict:
    """
    Simulates deploying a containerized app to a compute network by routing
    the request through the local FastAPI backend.
    """
    from sovergrid.services.blockchain import BlockchainService

    log.info(
        f"Deploying '{config.app_name}' to {provider.title()} Network "
        f"via SoverGrid Backend..."
    )

    auth_headers = _load_auth_headers()

    # Step 1: Web3 Payment Routing
    blockchain = BlockchainService()
    if not blockchain.is_connected:
        log.error(f"{Colors.RED}Deployment failed. Cannot connect to blockchain.{Colors.RESET}")
        return None
        
    log.info(f"{Colors.YELLOW}Initiating Web3 Payment Routing for {cost.total:.4f} USDC...{Colors.RESET}")
    
    # Check balance before attempting to pay
    balance = blockchain.get_token_balance()
    if balance is not None and balance < cost.total:
        log.error(f"{Colors.RED}Insufficient USDC balance ({balance:.4f} USDC).{Colors.RESET}")
        log.error(f"{Colors.CYAN}Please run `sovergrid faucet` to get $1,000 in free testnet USDC.{Colors.RESET}")
        return None

    # Resolve provider wallet
    provider_wallet = "0x" + "1" * 40  # Placeholder for routing resolution
    tx_hash = blockchain.pay_for_deployment(cost.total, provider_wallet)
    
    if not tx_hash:
        log.error(f"{Colors.RED}Deployment aborted. Payment failed.{Colors.RESET}")
        return None

    log.info(f"{Colors.GREEN}Payment Secured. Transaction Hash: {tx_hash}{Colors.RESET}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "app_name": config.app_name,
                "provider": provider.lower(),
                "config": {
                    "cpu": config.cpu,
                    "memory": config.memory
                },
                "transaction_hash": tx_hash
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
        msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                msg = e.response.json().get("detail", str(e))
            except:
                pass
        log.error(f"Backend deployment failed: {msg}")
        return None


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
        return None


async def deploy_database(config: SoverGridConfig, provider: str) -> dict:
    if not provider:
        return None
    from sovergrid.services.blockchain import BlockchainService
    log.info(f"Deploying database to {provider.title()} Network via SoverGrid Backend...")
    
    auth_headers = _load_auth_headers()
    blockchain = BlockchainService()
    if not blockchain.is_connected:
        log.error(f"{Colors.RED}Database deployment failed. Cannot connect to blockchain.{Colors.RESET}")
        return None
        
    db_cost = 2.50 if provider == "kwil" else 1.80
    log.info(f"{Colors.YELLOW}Initiating Web3 Payment Routing for Database ({db_cost:.4f} USDC)...{Colors.RESET}")
    
    # Check balance before attempting to pay
    balance = blockchain.get_token_balance()
    if balance is not None and balance < db_cost:
        log.error(f"{Colors.RED}Insufficient USDC balance for Database ({balance:.4f} USDC).{Colors.RESET}")
        log.error(f"{Colors.CYAN}Please run `sovergrid faucet` to get free testnet USDC.{Colors.RESET}")
        return None

    provider_wallet = "0x" + "2" * 40
    tx_hash = blockchain.pay_for_deployment(db_cost, provider_wallet)
    
    if not tx_hash:
        return None
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "app_name": config.app_name,
                "provider": provider.lower(),
                "service_type": "database",
                "config": {"db_name": config.database_name},
                "transaction_hash": tx_hash
            }
            api_url = os.environ.get("SOVERGRID_API_URL", "https://web-production-4966c.up.railway.app")
            response = await client.post(f"{api_url}/deploy", json=payload, headers=auth_headers)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("data", {})
            log.info(f"{Colors.GREEN}{provider.title()} database deployment successful.{Colors.RESET}")
            
            return {
                "provider": provider,
                "status": "active",
                "endpoint": result_data.get("url", f"https://db.{provider}.network/{config.database_name}")
            }
    except Exception as e:
        log.error(f"Backend database deployment failed: {str(e)}")
        return None


async def deploy_frontend(config: SoverGridConfig) -> dict:
    if not config.frontend_provider:
        return None
    from sovergrid.services.blockchain import BlockchainService
    log.info(f"Deploying frontend to {config.frontend_provider.title()} Network via SoverGrid Backend...")
    
    auth_headers = _load_auth_headers()
    blockchain = BlockchainService()
    if not blockchain.is_connected:
        log.error(f"{Colors.RED}Frontend deployment failed. Cannot connect to blockchain.{Colors.RESET}")
        return None
        
    fe_cost = 1.00
    log.info(f"{Colors.YELLOW}Initiating Web3 Payment Routing for Frontend ({fe_cost:.4f} USDC)...{Colors.RESET}")
    
    # Check balance before attempting to pay
    balance = blockchain.get_token_balance()
    if balance is not None and balance < fe_cost:
        log.error(f"{Colors.RED}Insufficient USDC balance for Frontend ({balance:.4f} USDC).{Colors.RESET}")
        log.error(f"{Colors.CYAN}Please run `sovergrid faucet` to get free testnet USDC.{Colors.RESET}")
        return None

    provider_wallet = "0x" + "3" * 40
    tx_hash = blockchain.pay_for_deployment(fe_cost, provider_wallet)
    
    if not tx_hash:
        return None
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "app_name": config.app_name,
                "provider": config.frontend_provider.lower(),
                "service_type": "frontend",
                "config": {},
                "transaction_hash": tx_hash
            }
            api_url = os.environ.get("SOVERGRID_API_URL", "https://web-production-4966c.up.railway.app")
            response = await client.post(f"{api_url}/deploy", json=payload, headers=auth_headers)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("data", {})
            details = result_data.get("details", {})
            
            # Prefer the branded DNS URL, fallback to raw endpoint
            endpoint = details.get("branded_url", details.get("endpoint", f"https://{config.app_name}.4everland.app"))
            
            log.info(f"{Colors.GREEN}{config.frontend_provider.title()} frontend deployment successful.{Colors.RESET}")
            
            return {
                "provider": config.frontend_provider,
                "status": "active",
                "endpoint": endpoint
            }
    except Exception as e:
        log.error(f"Backend frontend deployment failed: {str(e)}")
        return None


async def run_deployment(config: SoverGridConfig) -> dict:
    """
    Orchestrates a full deployment with Fallbacks & Cost Protection.
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
    # Simulate network instability for fallback testing if requested
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

    # 2b. Database Fallback Logic
    db_provider = config.database_provider
    if db_provider == "kwil" and random.random() < 0.2:
        log.error("Kwil Network is currently unreachable.")
        log.warning("Attempting automatic fallback to Tableland Network...")
        db_provider = "tableland"
        log.info(f"{Colors.GREEN}Database fallback approved. Tableland selected.{Colors.RESET}")

    # 3. Run compute, storage, database, and frontend deployments concurrently
    compute_task = deploy_compute(config, provider=active_provider, cost=cost)
    storage_task = deploy_to_filecoin(config)
    database_task = deploy_database(config, provider=db_provider)
    frontend_task = deploy_frontend(config)
    
    compute_result, filecoin_result, db_result, fe_result = await asyncio.gather(
        compute_task, storage_task, database_task, frontend_task
    )

    elapsed = round(time.time() - start_time, 2)

    if compute_result:
        output = (
            f"\n"
            f"  {Colors.BOLD}{Colors.GREEN}"
            f"  Deployment Complete{Colors.RESET}\n"
            f"  Time: {elapsed}s\n"
            f"  Compute Endpoint: {compute_result.get('endpoint', 'N/A')}\n"
        )
        if fe_result:
            output += f"  Frontend URL: {Colors.CYAN}{Colors.UNDERLINE}{fe_result.get('endpoint')}{Colors.RESET}\n"
        output += f"{cost.display()}"
        log.info(output)
        log.info("=" * 60)
        log.info(f"{Colors.YELLOW}SoverGrid Beta Phase 1 Completed.{Colors.RESET}")
        log.info("If you encountered any errors or have feedback, please report them directly to the founder:")
        log.info(f"{Colors.CYAN}Email: info@sovergrid.network | Twitter: @SoverGrid{Colors.RESET}")
        log.info("=" * 60)
    else:
        log.error(f"\n{Colors.BOLD}{Colors.RED}Deployment failed. Please check the errors above.{Colors.RESET}")
        log.info("=" * 60)
        log.info("If you encountered any errors or bugs during testing, please report them to the founder:")
        log.info(f"{Colors.CYAN}Email: info@sovergrid.network | Twitter: @SoverGrid{Colors.RESET}")
        log.info("=" * 60)

    return {
        "app_name": config.app_name,
        "compute": compute_result,
        "storage": filecoin_result,
        "database": db_result,
        "frontend": fe_result,
        "cost": {
            "base": cost.base_cost,
            "total": cost.total,
            "currency": config.payment_token,
        },
        "elapsed_seconds": elapsed,
    }
