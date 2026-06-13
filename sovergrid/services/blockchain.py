"""
SoverGrid Blockchain Service
Handles Web3 connections, wallet derivations, and smart contract reads/writes.
"""
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import ContractLogicError

from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)

# Default Sepolia RPC (same one from Hardhat config)
DEFAULT_RPC_URL = "https://sepolia.drpc.org"

# Load environment variables from the smart-contracts folder 
# (so we don't have to copy the .env around for now)
SMART_CONTRACTS_DIR = Path(__file__).parent.parent.parent.parent / "sovergrid-smart-contracts"
load_dotenv(dotenv_path=SMART_CONTRACTS_DIR / ".env")

class BlockchainService:
    """
    Connects to the Ethereum blockchain to query token balances and execute smart contracts.
    """
    def __init__(self, rpc_url: str = DEFAULT_RPC_URL):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # Inject PoA middleware for testnets like Sepolia
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key and not self.private_key.startswith("0x"):
            self.private_key = f"0x{self.private_key}"
            
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.token_abi = self._load_token_abi()

    def _load_token_abi(self) -> Optional[list]:
        """Loads the compiled SoverGridToken ABI from the Hardhat artifacts."""
        abi_path = SMART_CONTRACTS_DIR / "artifacts" / "contracts" / "SoverGridToken.sol" / "SoverGridToken.json"
        if not abi_path.exists():
            log.warning(f"Could not find token ABI at {abi_path}. Did you compile the smart contracts?")
            return None
            
        with open(abi_path, "r") as f:
            data = json.load(f)
            return data.get("abi")

    @property
    def is_connected(self) -> bool:
        """Checks if the Web3 provider is successfully connected to the blockchain."""
        return self.w3.is_connected()

    @property
    def wallet_address(self) -> Optional[str]:
        """Derives the public wallet address from the private key."""
        if not self.private_key:
            return None
        try:
            account = self.w3.eth.account.from_key(self.private_key)
            return account.address
        except Exception as e:
            log.error(f"Failed to derive wallet address from private key: {e}")
            return None

    def get_token_balance(self, address: str = None) -> Optional[float]:
        """
        Queries the blockchain for the $SVR token balance of the specified address.
        If no address is provided, defaults to the user's wallet address.
        """
        target_address = address or self.wallet_address
        if not target_address:
            log.error(f"{Colors.RED}No wallet address provided and PRIVATE_KEY not found in .env{Colors.RESET}")
            return None
            
        if not self.contract_address:
            log.error(f"{Colors.RED}CONTRACT_ADDRESS not found in .env. Please add it!{Colors.RESET}")
            return None

        if not self.token_abi:
            return None

        # Instantiate the smart contract
        checksum_address = self.w3.to_checksum_address(self.contract_address)
        target_checksum = self.w3.to_checksum_address(target_address)
        
        try:
            contract = self.w3.eth.contract(address=checksum_address, abi=self.token_abi)
            # Call the balanceOf function
            raw_balance = contract.functions.balanceOf(target_checksum).call()
            
            # The token has 18 decimals, so we divide by 1e18
            # We assume standard 18 decimals for ERC20
            decimals = contract.functions.decimals().call()
            formatted_balance = raw_balance / (10 ** decimals)
            
            return formatted_balance
        except Exception as e:
            log.error(f"{Colors.RED}Failed to fetch balance from blockchain: {e}{Colors.RESET}")
            return None
