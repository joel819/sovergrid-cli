"""
SoverGrid Base Service
Abstract base class that ALL services must inherit from.

This is the "Plugin Architecture" foundation. Every service
(compute, storage, ML, database, CDN) follows the exact same
pattern so they are all interchangeable and independently usable.

LEARNING NOTE FOR JOEL:
-----------------------
An Abstract Base Class (ABC) is like a "blueprint" or "contract."
It says: "If you want to be a SoverGrid service, you MUST have
these methods." If you forget to implement one, Python will
crash immediately and tell you what you forgot. This prevents
bugs from sneaking into production.
"""

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)


@dataclass
class ServiceResult:
    """
    Standard result object returned by every service.
    No matter which service runs, the output always looks the same.
    This makes it easy for the CLI to display results consistently.
    """
    service_name: str          # e.g., "compute", "storage", "ml_training"
    provider: str              # e.g., "akash", "filecoin", "bittensor"
    status: str                # e.g., "active", "pinned", "training"
    endpoint: str = ""         # URL or CID where the result lives
    cost_usd: float = 0.0     # How much this service cost
    metadata: dict = field(default_factory=dict)  # Extra provider-specific data
    elapsed_seconds: float = 0.0


class BaseService(ABC):
    """
    Abstract base class for all SoverGrid services.

    Every service MUST implement:
      - name          -> What is this service called?
      - validate()    -> Is the user's config valid for this service?
      - execute()     -> Run the actual service logic
      - estimate_cost() -> How much will this cost?

    Every service gets FOR FREE:
      - run()         -> The full pipeline (validate -> cost check -> execute)
      - Cost protection (auto-cancels if over budget)
      - Timing (automatically tracks how long the service took)
      - Logging (consistent output format)
    """

    def __init__(self, config: dict, max_budget: float = 5.00):
        """
        Args:
            config: The relevant section from sovergrid.yaml.
                    For compute, this is the 'compute:' block.
                    For ML, this is the 'ml:' block.
            max_budget: Maximum the user is willing to spend.
        """
        self.config = config
        self.max_budget = max_budget

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the service (e.g., 'Compute', 'ML Training')."""
        ...

    @abstractmethod
    async def validate(self) -> bool:
        """
        Check if the user's config has everything needed.
        Return True if valid, raise ConfigError or return False if not.
        """
        ...

    @abstractmethod
    async def execute(self) -> ServiceResult:
        """
        Run the actual service logic.
        This is where the real API calls will go in the future.
        Right now it's all mock/simulated.
        """
        ...

    @abstractmethod
    def estimate_cost(self) -> float:
        """
        Estimate the cost of this service in USD.
        In the future, this will query live pricing APIs.
        """
        ...

    async def run(self) -> Optional[ServiceResult]:
        """
        Full service pipeline. This is what the CLI calls.

        1. Validate the config
        2. Estimate the cost
        3. Check against the user's budget
        4. Execute the service
        5. Return the result with timing info

        You do NOT override this method. Override validate(),
        execute(), and estimate_cost() instead.
        """
        log.info(f"{Colors.BOLD}[{self.name}]{Colors.RESET} Starting...")

        # Step 1: Validate
        is_valid = await self.validate()
        if not is_valid:
            log.error(f"[{self.name}] Config validation failed.")
            return None

        # Step 2: Cost check
        estimated_cost = self.estimate_cost()
        if estimated_cost > self.max_budget:
            log.error(
                f"[{self.name}] Estimated cost (${estimated_cost:.4f}) "
                f"exceeds your max_budget (${self.max_budget:.4f}). Canceled."
            )
            return None

        log.info(
            f"[{self.name}] Estimated cost: ${estimated_cost:.4f} "
            f"(budget: ${self.max_budget:.4f})"
        )

        # Step 3: Execute
        start_time = time.time()
        result = await self.execute()
        result.elapsed_seconds = round(time.time() - start_time, 2)
        result.cost_usd = estimated_cost

        log.info(
            f"{Colors.GREEN}[{self.name}] Complete{Colors.RESET} "
            f"in {result.elapsed_seconds}s | "
            f"Cost: ${result.cost_usd:.4f}"
        )

        return result
