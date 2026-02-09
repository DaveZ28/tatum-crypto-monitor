

# Imports
import argparse

from dotenv import load_dotenv

from tatum_client import TatumClient
from analyze import summarize_tatum_transactions, convert_wei_to_eth

# Shorten long hashes/addresses for readability
def shorten_hash(tx_hash: str) -> str:
    if not tx_hash:
        return "n/a"
    return f"{tx_hash[:10]}…{tx_hash[-6:]}" if len(tx_hash) > 20 else tx_hash


def shorten_address(address: str) -> str:
    if not address:
        return "n/a"
    return f"{address[:6]}…{address[-4:]}" if len(address) > 14 else address


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Ethereum address monitor using Tatum APIs"
    )
    parser.add_argument(
        "--address",
        required=True,
        help="Ethereum address to monitor (0x...)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of recent items to fetch",
    )

    args = parser.parse_args()

    try:
        client = TatumClient()

        # 1) Get ETH balance via RPC Gateway
        balance_wei = client.get_eth_balance_wei(args.address)
        balance_eth = convert_wei_to_eth(balance_wei)

        # 2) Get transaction history via Data API
        transactions = client.get_transaction_history(
            ethereum_address=args.address,
            page_size=args.limit,
            chain="ethereum-mainnet",
        )

        # 3) Summarize transactions
        summary = summarize_tatum_transactions(transactions)

    except Exception as exc:
        print("\n❌ Error while running monitor:")
        print(str(exc))
        return 1

    # ---- Output ----
    print(f"\nAddress: {args.address}")
    print(f"ETH balance (RPC): {balance_eth:.6f} ETH")
    print(f"Items fetched: {summary.total_items}")
    print(f"Incoming: {summary.incoming_count} | Outgoing: {summary.outgoing_count}")
    print(
          f"Native ETH in: {summary.native_eth_in:.9f} ETH | "
          f"Native ETH out: {summary.native_eth_out:.9f} ETH"
         )
    print(f"Token-related transfers: {summary.token_related_transfers}")
    print(f"Last activity (UTC): {summary.last_activity_iso or 'n/a'}")

    print("\nRecent activity (Tatum history):")
    print("subtype   | type     | amount          | counter         | block      | hash")
    print("-" * 96)

    for tx in transactions[: args.limit]:
        subtype = (tx.get("transactionSubtype") or "n/a").ljust(8)
        tx_type = (tx.get("transactionType") or "n/a").ljust(8)
        amount = str(tx.get("amount") or "0").rjust(14)
        counter = shorten_address(tx.get("counterAddress") or "")
        block = str(tx.get("blockNumber") or "n/a").rjust(9)
        tx_hash = shorten_hash(tx.get("hash") or "")

        print(f"{subtype} | {tx_type} | {amount} | {counter:14} | {block} | {tx_hash}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
