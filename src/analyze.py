

# Imports
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional


@dataclass
class TransactionSummary:
    total_items: int
    incoming_count: int
    outgoing_count: int
    native_eth_in: Decimal
    native_eth_out: Decimal
    token_related_transfers: int
    last_activity_iso: Optional[str]


def convert_wei_to_eth(wei: int) -> Decimal:
    return Decimal(wei) / Decimal(10**18)


def _to_decimal(value: Any) -> Decimal:
    """
    Safely convert string/number to Decimal.
    Tatum returns 'amount' as string.
    """
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(0)


def _timestamp_ms_to_iso(timestamp_ms: Any) -> Optional[str]:
    """
    Convert milliseconds timestamp to ISO 8601 UTC string.
    """
    if timestamp_ms is None:
        return None

    try:
        timestamp_int = int(timestamp_ms)
        dt = datetime.fromtimestamp(timestamp_int / 1000.0, tz=timezone.utc)
        return dt.isoformat()
    except Exception:
        return None


def summarize_tatum_transactions(
    transaction_list: List[Dict[str, Any]],
) -> TransactionSummary:
    incoming_count = 0
    outgoing_count = 0
    native_eth_in = Decimal(0)
    native_eth_out = Decimal(0)
    token_transfers = 0
    last_timestamp_ms: Optional[int] = None

    for tx in transaction_list:
        transaction_subtype = tx.get("transactionSubtype")  # incoming / outgoing
        transaction_type = tx.get("transactionType")        # native / fungible / etc.
        amount = _to_decimal(tx.get("amount"))
        timestamp_ms = tx.get("timestamp")

        # Count incoming vs outgoing
        if transaction_subtype == "incoming":
            incoming_count += 1
        elif transaction_subtype == "outgoing":
            outgoing_count += 1

        # Sum native ETH transfers separately
        if transaction_type == "native":
            if transaction_subtype == "incoming":
                native_eth_in += amount
            elif transaction_subtype == "outgoing":
                # Use absolute value in case of negative amounts
                native_eth_out += abs(amount)

        # Token-related transfer (most reliable: tokenAddress present)
        if tx.get("tokenAddress"):
            token_transfers += 1

        # Track latest activity timestamp (ms)
        try:
            ts_int = int(timestamp_ms) if timestamp_ms is not None else None
        except Exception:
            ts_int = None

        if ts_int is not None and (
            last_timestamp_ms is None or ts_int > last_timestamp_ms
        ):
            last_timestamp_ms = ts_int

    last_activity_iso = _timestamp_ms_to_iso(last_timestamp_ms)

    return TransactionSummary(
        total_items=len(transaction_list),
        incoming_count=incoming_count,
        outgoing_count=outgoing_count,
        native_eth_in=native_eth_in,
        native_eth_out=native_eth_out,
        token_related_transfers=token_transfers,
        last_activity_iso=last_activity_iso,
    )

