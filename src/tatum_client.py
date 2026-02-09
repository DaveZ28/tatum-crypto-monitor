import os
import requests
from typing import Any, Dict, List, Optional


class TatumClient:
    """
    Small wrapper around Tatum APIs:
    - RPC Gateway for ETH balance
    - Data API v4 for transaction history
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TATUM_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "Missing TATUM_API_KEY. Set it in a .env file or environment variables."
            )

        self.session = requests.Session()
        self.session.headers.update({"x-api-key": self.api_key})

    def get_eth_balance_wei(self, ethereum_address: str) -> int:
        """
        Get ETH balance in wei using Tatum's Ethereum RPC Gateway.
        """
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

        # Tatum returns a list directly (as you saw in your output)
        if isinstance(response_json, list):
            return response_json

        # Fallback in case of wrapped responses in the future
        if isinstance(response_json, dict):
            for key in ("data", "transactions", "result"):
                if key in response_json and isinstance(response_json[key], list):
                    return response_json[key]

        return []

