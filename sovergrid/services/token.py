"""
SoverGrid Token Service
Deploys a standard ERC-20 token contract to the blockchain on behalf of a user.

The user provides:
  - Token name, symbol, and supply via `sovergrid token` CLI command
  - Their PRIVATE_KEY in their local .env

SoverGrid handles:
  - Compiling and deploying the ERC-20 contract
  - Returning the contract address and transaction hash to the user
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Standard minimal ERC-20 ABI (for verification reads after deployment)
ERC20_ABI = [
    {"inputs": [{"name": "_name", "type": "string"}, {"name": "_symbol", "type": "string"}, {"name": "_supply", "type": "uint256"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]

# Minimal ERC-20 bytecode — compiled from OpenZeppelin ERC-20 standard.
# This is the deployment bytecode for a basic mintable ERC-20.
# Replace with a Hardhat-compiled artifact in production for full verification.
ERC20_BYTECODE = "0x608060405234801561001057600080fd5b506040516200178b3803806200178b83398101604081905261003191620001db565b8251610044906003906020860190610066565b50815161005890600490602085019061006...<truncated_for_safety_use_hardhat_in_prod>"

NETWORK_RPC = {
    "sepolia": "https://sepolia.drpc.org",
    "mainnet": "https://eth-mainnet.g.alchemy.com/v2/",  # Requires ALCHEMY_KEY
    "polygon": "https://polygon-rpc.com",
}


class TokenService:
    """
    Deploys an ERC-20 token contract to the blockchain.
    
    In production, this reads the compiled artifact from the sovergrid-smart-contracts
    Hardhat project. For now it uses a pre-compiled bytecode stub and prints
    clear instructions for the user to proceed.
    """

    def __init__(
        self,
        token_name: str,
        token_symbol: str,
        token_supply: int,
        network: str = "sepolia",
    ):
        self.token_name = token_name
        self.token_symbol = token_symbol.upper()
        self.token_supply = token_supply
        self.network = network

        # Load .env from project root or smart contracts dir
        load_dotenv()
        smart_contracts_env = Path(__file__).parent.parent.parent.parent / "sovergrid-smart-contracts" / ".env"
        if smart_contracts_env.exists():
            load_dotenv(dotenv_path=smart_contracts_env)

        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key and not self.private_key.startswith("0x"):
            self.private_key = f"0x{self.private_key}"

    async def deploy(self) -> dict:
        """
        Main entry point. Attempts to deploy the ERC-20 contract.
        Falls back to a Hardhat deploy instruction if Web3 fails.
        """
        try:
            from web3 import Web3
            from web3.middleware import ExtraDataToPOAMiddleware
        except ImportError:
            return {
                "status": "error",
                "error": "web3 is not installed. Run: pip install web3"
            }

        if not self.private_key:
            return {
                "status": "error",
                "error": (
                    "No PRIVATE_KEY found in your .env file.\n"
                    "  Add: PRIVATE_KEY=your_wallet_private_key\n"
                    "  Your wallet needs ETH for gas to deploy the contract."
                )
            }

        rpc_url = NETWORK_RPC.get(self.network, NETWORK_RPC["sepolia"])
        w3 = Web3(Web3.HTTPProvider(rpc_url))

        if self.network in ("sepolia", "polygon"):
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not w3.is_connected():
            return {
                "status": "error",
                "error": f"Could not connect to the {self.network} network. Check your internet."
            }

        account = w3.eth.account.from_key(self.private_key)
        wallet_address = account.address

        log.info(f"  Deploying from wallet: {Colors.CYAN}{wallet_address}{Colors.RESET}")
        log.info(f"  Network: {self.network}")
        log.info(f"  Token: {self.token_name} ({self.token_symbol}) — Supply: {self.token_supply:,}")

        # Try to load the compiled artifact from the Hardhat project
        artifact = self._load_hardhat_artifact()
        if not artifact:
            # Fall back to Hardhat deploy instruction
            return self._hardhat_fallback()

        contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
        supply_with_decimals = self.token_supply * (10 ** 18)

        try:
            nonce = w3.eth.get_transaction_count(wallet_address)
            tx = contract.constructor(
                self.token_name,
                self.token_symbol,
                supply_with_decimals
            ).build_transaction({
                "from": wallet_address,
                "nonce": nonce,
                "gas": 2000000,
                "gasPrice": w3.eth.gas_price,
            })

            signed = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

            log.info(f"  {Colors.YELLOW}Transaction submitted. Waiting for confirmation...{Colors.RESET}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            return {
                "status": "success",
                "contract_address": receipt.contractAddress,
                "tx_hash": tx_hash.hex(),
                "network": self.network,
                "token_name": self.token_name,
                "token_symbol": self.token_symbol,
                "token_supply": self.token_supply,
                "deployer": wallet_address,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _load_hardhat_artifact(self) -> Optional[dict]:
        """
        Looks for the compiled SoverGridToken artifact from the Hardhat project.
        Returns None if not found (falls back to Hardhat CLI instructions).
        """
        artifact_path = (
            Path(__file__).parent.parent.parent.parent
            / "sovergrid-smart-contracts"
            / "artifacts"
            / "contracts"
            / "SoverGridToken.sol"
            / "SoverGridToken.json"
        )
        if not artifact_path.exists():
            return None

        with open(artifact_path, "r") as f:
            return json.load(f)

    def _hardhat_fallback(self) -> dict:
        """
        If the Hardhat artifact is not compiled yet, return clear instructions
        for the user to run Hardhat themselves.
        """
        log.info(
            f"\n  {Colors.YELLOW}Compiled contract not found.{Colors.RESET}\n"
            f"  To deploy your token, run these commands first:\n\n"
            f"  {Colors.CYAN}cd sovergrid-smart-contracts{Colors.RESET}\n"
            f"  {Colors.CYAN}npm install{Colors.RESET}\n"
            f"  {Colors.CYAN}npx hardhat compile{Colors.RESET}\n"
            f"  {Colors.CYAN}npx hardhat run scripts/deploy.js --network {self.network}{Colors.RESET}\n\n"
            f"  Then run {Colors.CYAN}sovergrid token{Colors.RESET} again — it will use the compiled artifact."
        )
        return {
            "status": "error",
            "error": "Compiled contract artifact not found. See instructions above."
        }
