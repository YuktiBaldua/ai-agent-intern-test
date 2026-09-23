from app.orders import OrderLookup


def test_order_id_is_normalized():
    store = OrderLookup()
    result = store.lookup(" ord - 1007 ")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"


def test_shipped_order_returns_safe_tracking_data():
    store = OrderLookup()
    result = store.lookup("ORD-1007")

    assert result["found"] is True
    assert result["status"] == "shipped"
    assert result["carrier"] == "UPS"
    assert result["tracking_number"]


def test_cancelled_order_does_not_expose_stale_eta():
    store = OrderLookup()
    result = store.lookup("ORD-1004")

    assert result["found"] is True
    assert result["status"] == "cancelled"
    assert "estimated_delivery" not in result


def test_unknown_order_is_not_invented():
    store = OrderLookup()
    result = store.lookup("ORD-9999")

    assert result["found"] is False
    assert result["reason"] == "order_not_found"
    assert result["order_id"] == "ORD-9999"


def test_missing_order_id_is_handled_safely():
    store = OrderLookup()
    result = store.lookup("")

    assert result["found"] is False
    assert result["reason"] == "missing_order_id"


def test_sensitive_order_fields_are_not_exposed():
    store = OrderLookup()
    result = store.lookup("ORD-1007")

    serialized = str(result).lower()

    assert "@" not in serialized
    assert "risk_score" not in serialized
    assert "internal_note" not in serialized
    assert "shipping_address" not in serialized
