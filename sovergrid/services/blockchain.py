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

# Load environment variables — two-step priority:
#   1. CWD .env — works for anyone who installs via `pip install sovergrid`
#      and keeps a .env in their project root (the common case).
#   2. Smart-contracts sibling dir .env — used during local monorepo development.
#      Silently skipped if the path doesn't exist (e.g., on PyPI installs).
load_dotenv()  # fallback: CWD .env
SMART_CONTRACTS_DIR = Path(__file__).parent.parent.parent.parent / "sovergrid-smart-contracts"
load_dotenv(dotenv_path=SMART_CONTRACTS_DIR / ".env")  # override: smart-contracts .env

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
            
        self.token_address = os.getenv("CONTRACT_ADDRESS")
        self.mock_usdc_address = os.getenv("MOCK_USDC_ADDRESS", self.token_address)
        self.aggregator_address = os.getenv("AGGREGATOR_ADDRESS")
        self.token_abi = self._load_token_abi()
        self.mock_usdc_abi = self._load_mock_usdc_abi()
        self.aggregator_abi = self._load_aggregator_abi()

    def _load_token_abi(self) -> Optional[list]:
        """Loads the compiled SoverGridToken ABI from the Hardhat artifacts."""
        abi_path = SMART_CONTRACTS_DIR / "artifacts" / "contracts" / "SoverGridToken.sol" / "SoverGridToken.json"
        if not abi_path.exists():
            log.warning(f"Could not find token ABI at {abi_path}. Did you compile the smart contracts?")
            return None
            
        with open(abi_path, "r") as f:
            data = json.load(f)
            return data.get("abi")

    def _load_mock_usdc_abi(self) -> Optional[list]:
        """Loads the compiled MockUSDC ABI from the Hardhat artifacts."""
        abi_path = SMART_CONTRACTS_DIR / "artifacts" / "contracts" / "MockUSDC.sol" / "MockUSDC.json"
        if not abi_path.exists():
            log.warning(f"Could not find MockUSDC ABI at {abi_path}.")
            return None
            
        with open(abi_path, "r") as f:
            data = json.load(f)
            return data.get("abi")

    def _load_aggregator_abi(self) -> Optional[list]:
        """Loads the compiled SoverGridAggregator ABI from the Hardhat artifacts."""
        abi_path = SMART_CONTRACTS_DIR / "artifacts" / "contracts" / "SoverGridAggregator.sol" / "SoverGridAggregator.json"
        if not abi_path.exists():
            log.warning(f"Could not find aggregator ABI at {abi_path}.")
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
            
        if not self.token_address:
            log.error(f"{Colors.RED}CONTRACT_ADDRESS not found in .env. Please add it!{Colors.RESET}")
            return None

        if not self.token_abi:
            return None

        # Instantiate the smart contract
        checksum_address = self.w3.to_checksum_address(self.token_address)
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

    def pay_for_deployment(self, amount: float, provider_wallet: str) -> Optional[str]:
        """
        Executes the Web3 "Pay-Then-Deploy" pattern.
        1. Approves the Aggregator contract to spend USDC.
        2. Calls payForDeployment on the Aggregator, which routes the flat SaaS fee
           and sends the remainder to the provider.
        Returns the transaction hash if successful.
        """
        if not self.private_key or not self.wallet_address:
            log.error(f"{Colors.RED}Cannot process payment. No wallet found.{Colors.RESET}")
            return None
            
        if not self.mock_usdc_address or not self.aggregator_address:
            log.error(f"{Colors.RED}Missing MOCK_USDC_ADDRESS or AGGREGATOR_ADDRESS in .env{Colors.RESET}")
            return None
            
        if not self.mock_usdc_abi or not self.aggregator_abi:
            log.error(f"{Colors.RED}Missing ABIs. Compile the contracts first.{Colors.RESET}")
            return None

        try:
            checksum_usdc = self.w3.to_checksum_address(self.mock_usdc_address)
            checksum_aggregator = self.w3.to_checksum_address(self.aggregator_address)
            checksum_provider = self.w3.to_checksum_address(provider_wallet)
            
            usdc_contract = self.w3.eth.contract(address=checksum_usdc, abi=self.mock_usdc_abi)
            aggregator_contract = self.w3.eth.contract(address=checksum_aggregator, abi=self.aggregator_abi)
            
            decimals = usdc_contract.functions.decimals().call()
            raw_amount = int(amount * (10 ** decimals))

            # Fetch dynamic gas prices
            base_fee = self.w3.eth.get_block('latest').get('baseFeePerGas', self.w3.to_wei('1', 'gwei'))
            max_priority = self.w3.eth.max_priority_fee
            max_fee = int(base_fee * 1.5) + max_priority

            # Step 1: Approve Aggregator to spend USDC
            log.info(f"{Colors.YELLOW}Approving {amount} USDC for payment...{Colors.RESET}")
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            # Estimate gas for approval
            approve_gas = usdc_contract.functions.approve(checksum_aggregator, raw_amount).estimate_gas({'from': self.wallet_address})
            
            approve_txn = usdc_contract.functions.approve(
                checksum_aggregator, raw_amount
            ).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': int(approve_gas * 1.2),
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': max_priority,
                'nonce': nonce,
            })
            
            signed_approve = self.w3.eth.account.sign_transaction(approve_txn, private_key=self.private_key)
            tx_hash_approve = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)
            
            # Wait for approval receipt
            self.w3.eth.wait_for_transaction_receipt(tx_hash_approve)
            log.info(f"{Colors.GREEN}USDC approval successful.{Colors.RESET}")
            
            # Step 2: Call payForDeployment (SaaS Fee Model)
            log.info(f"{Colors.YELLOW}Processing deployment payment via USDC SaaS markup...{Colors.RESET}")
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            pay_gas = aggregator_contract.functions.payForDeployment(
                checksum_usdc, raw_amount, checksum_provider
            ).estimate_gas({'from': self.wallet_address})
            
            pay_txn = aggregator_contract.functions.payForDeployment(
                checksum_usdc, raw_amount, checksum_provider
            ).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': int(pay_gas * 1.2),
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': max_priority,
                'nonce': nonce,
            })
            
            signed_pay = self.w3.eth.account.sign_transaction(pay_txn, private_key=self.private_key)
            tx_hash_pay = self.w3.eth.send_raw_transaction(signed_pay.raw_transaction)
            
            # Wait for payment receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_pay)
            
            if receipt.status == 1:
                log.info(f"{Colors.GREEN}Payment successful! Hash: {self.w3.to_hex(tx_hash_pay)}{Colors.RESET}")
                return self.w3.to_hex(tx_hash_pay)
            else:
                log.error(f"{Colors.RED}Payment transaction failed.{Colors.RESET}")
                return None
                
        except ContractLogicError as e:
            log.error(f"{Colors.RED}Smart Contract Logic Error: {e}{Colors.RESET}")
            return None
        except Exception as e:
            log.error(f"{Colors.RED}Failed to process blockchain payment: {e}{Colors.RESET}")
            return None

    def request_faucet_usdc(self, target_wallet: str) -> tuple[bool, Optional[str]]:
        """
        Calls the faucet() function on the MockUSDC contract.
        """
        if not self.private_key or not self.wallet_address:
            log.error(f"{Colors.RED}Cannot process faucet. No wallet found.{Colors.RESET}")
            return False, None
            
        if not self.mock_usdc_address or not self.mock_usdc_abi:
            log.error(f"{Colors.RED}Missing MOCK_USDC_ADDRESS in .env or missing ABI.{Colors.RESET}")
            return False, None

        try:
            checksum_usdc = self.w3.to_checksum_address(self.mock_usdc_address)
            usdc_contract = self.w3.eth.contract(address=checksum_usdc, abi=self.mock_usdc_abi)
            
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            # The target_wallet argument is not used in the contract because faucet() mints to msg.sender
            # We assume target_wallet is the same as the derived wallet_address
            if target_wallet.lower() != self.wallet_address.lower():
                log.error(f"{Colors.RED}Faucet can only mint to the calling wallet.{Colors.RESET}")
                return False, None
            
            # Fetch dynamic gas prices
            base_fee = self.w3.eth.get_block('latest').get('baseFeePerGas', self.w3.to_wei('1', 'gwei'))
            max_priority = self.w3.eth.max_priority_fee
            max_fee = int(base_fee * 1.5) + max_priority
            
            faucet_gas = usdc_contract.functions.faucet().estimate_gas({'from': self.wallet_address})
            
            faucet_txn = usdc_contract.functions.faucet().build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': int(faucet_gas * 1.2),
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': max_priority,
                'nonce': nonce,
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(faucet_txn, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return True, self.w3.to_hex(tx_hash)
            else:
                return False, None
                
        except ContractLogicError as e:
            log.error(f"{Colors.RED}Faucet Smart Contract Logic Error (Maybe cooldown?): {e}{Colors.RESET}")
            return False, None
        except Exception as e:
            log.error(f"{Colors.RED}Failed to process faucet request: {e}{Colors.RESET}")
            return False, None
