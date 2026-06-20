"""
SoverGrid Database Service
Handles connecting to decentralized database networks.

STANDALONE USAGE:
    sovergrid db create   (provisions a decentralized database)
    sovergrid db connect  (gets connection credentials)

PROVIDERS:
    - Kwil (decentralized SQL database)
    - Tableland (decentralized on-chain SQL database, tables are ERC721 NFTs)

LEARNING NOTE FOR JOEL:
-----------------------
Traditional databases (PostgreSQL on AWS RDS, MongoDB on Atlas)
are centralized. A government can subpoena Amazon and get all
the data. Decentralized databases store data across a network
of nodes, so no single entity controls the data.

This service is completely standalone. A user who only needs
a decentralized database doesn't touch compute, storage, or ML.
"""

import asyncio
import random

from sovergrid.services.base import BaseService, ServiceResult
from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Supported database providers
DB_PROVIDERS = {
    "kwil": {
        "type": "SQL",
        "price_per_month": 2.50,
        "description": "Decentralized SQL database with ACID compliance",
    },
    "tableland": {
        "type": "SQL",
        "price_per_month": 2.00,
        "description": "Decentralized on-chain SQL database (tables are ERC721 NFTs)",
    },
}


class DatabaseService(BaseService):
    """
    Provisions and connects to a decentralized database.

    Config expected (from sovergrid.yaml):
        database:
          provider: "kwil"
          name: "my_app_db"
          schema: "./schema.sql"
    """

    @property
    def name(self) -> str:
        return "Database"

    @property
    def provider(self) -> str:
        return self.config.get("provider", "kwil")

    @property
    def db_name(self) -> str:
        return self.config.get("name", "sovergrid_db")

    @property
    def schema_path(self) -> str:
        return self.config.get("schema", "")

    async def validate(self) -> bool:
        """Validates the database config."""
        provider = self.provider
        if provider not in DB_PROVIDERS:
            log.error(
                f"[Database] Unknown provider '{provider}'. "
                f"Supported: {', '.join(DB_PROVIDERS.keys())}"
            )
            return False

        if not self.db_name:
            log.error("[Database] Database name is required.")
            return False

        provider_info = DB_PROVIDERS[provider]
        log.info(
            f"[Database] Config valid: {provider} ({provider_info['type']}) | "
            f"DB: {self.db_name}"
        )
        return True

    def estimate_cost(self) -> float:
        """Estimates monthly database cost."""
        provider_info = DB_PROVIDERS.get(self.provider, DB_PROVIDERS["kwil"])
        return provider_info["price_per_month"]

    async def execute(self) -> ServiceResult:
        """
        Provisions a decentralized database instance.

        FUTURE: Replace with real Kwil SDK calls or Tableland smart contract interactions.
        """
        provider = self.provider
        provider_info = DB_PROVIDERS[provider]

        log.info(f"[Database] Connecting to {provider.title()} Network...")
        await asyncio.sleep(random.uniform(0.3, 0.6))

        log.info(
            f"[Database] Provisioning {provider_info['type']} database "
            f"'{self.db_name}'..."
        )
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if self.schema_path:
            log.info(f"[Database] Applying schema from {self.schema_path}...")
            await asyncio.sleep(random.uniform(0.2, 0.4))

        # Generate the connection string based on the active provider
        generated_connection_string = (
            f"postgresql://admin:sovergrid_secure_pwd@{provider_info['gateway']}"
            f":{random.randint(5432, 5999)}/{db_name}"
        )
        
        # In a real environment, wait for node provisioning confirmation
        await asyncio.sleep(2.5)

        log.info(
            f"  {Colors.GREEN}✅ Database provisioning "
            f"successful.{Colors.RESET}"
        )

        return ServiceResult(
            status="success",
            provider=self.provider,
            cost_usd=cost_usd,
            endpoint=generated_connection_string,
            metadata={
                "db_name": db_name,
                "db_type": db_type,
                "connection_string": generated_connection_string,
            },
        )
