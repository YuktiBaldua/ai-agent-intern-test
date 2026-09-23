import json
import re
from pathlib import Path
from typing import Any


class OrderLookup:
    """
    Safe order lookup for the Aster & Row support agent.

    The model should only receive customer-safe fields returned by
    this class. Internal fields such as risk scores, warehouse notes,
    support tags, email addresses, and shipping addresses are never
    exposed.
    """

    def __init__(self, orders_path: str = "data/orders.json"):
        self.orders_path = Path(orders_path)
        self.orders: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        with self.orders_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        order_list = data.get("orders", [])

        if not isinstance(order_list, list):
            raise ValueError("Expected 'orders' to be a list.")

        self.orders = {}

        for order in order_list:
            order_id = order.get("order_id")

            if not order_id:
                continue

            normalized_id = self.normalize_order_id(order_id)
            self.orders[normalized_id] = order

    @staticmethod
    def normalize_order_id(order_id: str) -> str:
        """
        Normalize user-provided order IDs.

        Example:
            ' ord-1007 ' -> 'ORD-1007'
            'ORD-1007'  -> 'ORD-1007'
        """
        if not isinstance(order_id, str):
            return ""

        return re.sub(r"\s+", "", order_id).upper()

    def lookup(self, order_id: str) -> dict[str, Any]:
        """
        Look up an order and return only customer-safe information.
        """

        normalized_id = self.normalize_order_id(order_id)

        if not normalized_id:
            return {
                "found": False,
                "reason": "missing_order_id",
            }

        order = self.orders.get(normalized_id)

        if order is None:
            return {
                "found": False,
                "reason": "order_not_found",
                "order_id": normalized_id,
            }

        status = str(order.get("status", "")).lower()

        result: dict[str, Any] = {
            "found": True,
            "order_id": order.get("order_id"),
            "status": status,
            "customer_safe_message": order.get(
                "customer_safe_message"
            ),
        }

        # Carrier/tracking information is useful when the order
        # has actually shipped.
        if status == "shipped":
            result["carrier"] = order.get("carrier")
            result["tracking_number"] = order.get("tracking_number")

            # Never invent an ETA. Only return it when the dataset
            # actually provides one.
            if order.get("estimated_delivery"):
                result["estimated_delivery"] = order.get(
                    "estimated_delivery"
                )

        # For delivered orders, expose the delivered date if present.
        elif status == "delivered":
            if order.get("delivered_at"):
                result["delivered_at"] = order.get("delivered_at")

        # For cancelled/returned orders, deliberately do NOT expose
        # stale shipping or estimated-delivery fields.
        elif status in {"cancelled", "returned"}:
            result["customer_safe_message"] = order.get(
                "customer_safe_message"
            )

        return result
