from app.retrieval import KnowledgeBase


def test_active_return_policy_beats_legacy_policy():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search("What is the standard return window?", top_k=6)

    filenames = [result["chunk"].filename for result in results]

    assert "01-returns-policy-current.md" in filenames


def test_international_shipping_retrieves_supported_destinations():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "Can you ship to Germany?",
        top_k=6,
        customer_only=True,
    )

    assert any(
        result["chunk"].filename == "06-international-shipping.md"
        and result["chunk"].heading == "Supported destinations"
        for result in results
    )


def test_breeze_tumbler_conflict_sources_are_retrievable():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "Can the Breeze Tumbler go in the dishwasher?",
        top_k=6,
        customer_only=True,
    )

    filenames = {result["chunk"].filename for result in results}

    assert "11-product-care.md" in filenames
    assert "12-breeze-tumbler-product-card.md" in filenames


def test_internal_migration_note_is_not_customer_eligible():
    kb = KnowledgeBase("knowledge-base")

    results = kb.search(
        "60 day return policy migration notes",
        top_k=6,
        customer_only=True,
    )

    assert all(
        result["chunk"].filename != "14-internal-content-migration-notes.md"
        for result in results
    )
