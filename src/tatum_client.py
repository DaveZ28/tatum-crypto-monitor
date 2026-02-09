

# Imports
import os
from typing import Any, Dict, List, Optional

import requests


# Defining class object
class TatumClient:
    """
    TatumClient
    - Using RPC Gateway for ETH balance
    - Using Data API v4 for transaction history
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TATUM_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "Missing TATUM_API_KEY! Set it in a .env file or environment variables."
            )
        
        # Reusable HTTP session:
        # - keeps connections open (faster)
        # - central place for headers (API key)
        self.session = requests.Session()
        # Setting the API key globally
        self.session.headers.update({"x-api-key": self.api_key})
    

    @staticmethod
    def _validate_eth_address(ethereum_address: str) -> None:
        """
        Minimal validation.
        Prevents obvious mistakes before calling APIs.
        """
        if not isinstance(ethereum_address, str):
            raise ValueError("Ethereum address must be a string.")

        address = ethereum_address.strip()
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError(
                f"Invalid Ethereum address format: '{ethereum_address}'. "
                "Expected 42 chars starting with 0x."
            )
    # Function that takes an Ethereum address and returns the balance
    def get_eth_balance_wei(self, ethereum_address: str) -> int:
        """
        Get ETH balance in wei using Tatum's Ethereum RPC Gateway.
        """

        # Call validation method
        self._validate_eth_address(ethereum_address)

        rpc_url = "https://ethereum-mainnet.gateway.tatum.io/"

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [ethereum_address, "latest"],
            "id": 1,
        }

        response = self.session.post(
            rpc_url,
            json=payload,
            headers={"content-type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()

        response_json = response.json()

        if "error" in response_json:
            raise RuntimeError(f"RPC error: {response_json['error']}")

        # Result is hex string, convert to integer wei
        return int(response_json["result"], 16)


    # Fetches recent transaction history via Tatum’s Data API
    def get_transaction_history(
        self,
        ethereum_address: str,
        page_size: int = 20,
        chain: str = "ethereum-mainnet",
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent transaction history from Tatum Data API v4.
        Returns a list of transaction objects.
        """

        # Call validation method
        self._validate_eth_address(ethereum_address)

        data_api_url = "https://api.tatum.io/v4/data/transaction/history"

        params = {
            "chain": chain,
            "addresses": ethereum_address,
            "pageSize": page_size,
        }

        response = self.session.get(
            data_api_url,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        response_json = response.json()

        # Tatum returns a list
        if isinstance(response_json, list):
            return response_json

        # Fallback in case of wrapped responses in the future
        if isinstance(response_json, dict):
            for key in ("data", "transactions", "result"):
                if key in response_json and isinstance(response_json[key], list):
                    return response_json[key]

        return []

