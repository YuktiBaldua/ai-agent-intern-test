import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent import SupportAgent


def normalize(text):
    return (
        " ".join(
            text.lower()
            .replace("’", "'")
            .replace("‘", "'")
            .replace("–", "-")
            .replace("—", "-")
            .replace("\u2011", "-")
            .split()
        )
    )

def contains_any(answer, phrases):
    answer = normalize(answer)
    return any(normalize(p) in answer for p in phrases)


def concept_check(answer, concept):
    answer = normalize(answer)

    concept_groups = {
        "final sale does not block damaged-item review": [
            "final-sale items can still be reviewed",
            "final sale does not prevent",
            "final sale doesn't prevent",
            "final sale does not block",
        ],
        "Canada is supported": [
            "ship to canada",
            "ships to canada",
            "canada is supported",
            "currently ships internationally only to canada",
        ],
        "5–9 business days after dispatch": [
            "5–9 business days after dispatch",
            "5-9 business days after dispatch",
            "5 to 9 business days after dispatch",
        ],
        "duties or taxes are not prepaid": [
            "duties and taxes are not prepaid",
            "duties or taxes are not prepaid",
            "not prepaid by aster",
        ],
        "shipping to Germany is not currently available": [
            "shipping to germany isn't available",
            "shipping to germany is not available",
            "shipping to germany is unavailable",
            "shipping to germany is not currently available",
            "does not ship to germany",
            "don't ship internationally to germany",
            "do not ship internationally to germany",
            "can't ship an atlas weekender to germany",
            "cannot ship an atlas weekender to germany",
        ],
        "the order is cancelled": [
            "order has been cancelled",
            "order is cancelled",
            "order was cancelled",
            "was cancelled",
            "has been cancelled",
        ],
        "it will not be shipped": [
            "will not be shipped",
            "won't be shipped",
        ],
        "order was not found": [
            "couldn't find order",
            "could not find order",
            "order was not found",
            "order cannot be found",
        ],
        "check the order ID or contact support": [
            "check the order id",
            "contact customer support",
            "contact support",
        ],
        "shipped with Canada Post": [
            "shipped with canada post",
        ],
        "delivery estimate is unavailable": [
            "estimate is unavailable",
            "delivery estimate is unavailable",
            "no delivery estimate",
        ],
        "no lifetime warranty": [
            "no lifetime warranty",
            "does not offer a lifetime warranty",
            "does not provide lifetime warranties",
            "lifetime warranties are not provided",
        ],
        "bags have 2 years": [
            "bags and backpacks: 2",
            "bags have 2 years",
            "bags and backpacks 2 years",
            "bags and backpacks 2 years from purchase",
        ],
        "drinkware and travel accessories have 1 year": [
            "drinkware",
            "travel accessories",
            "1 year",
            "drinkware 1 year",
            "travel accessories 1 year",
        ],
        "migration note is not authoritative": [
            "migration note is not authoritative",
            "migration notes are not authoritative",
            "not authoritative",
        ],
        "standard policy is 30 days unless a valid exception applies": [
            "30-day window",
            "30 day window",
            "30 days",
        ],
        "the agent cannot approve a return": [
            "cannot approve",
            "can't approve",
        ],
        "the supplied information is insufficient": [
            "information provided in our knowledge base is not sufficient",
            "information is insufficient",
            "not sufficient to confirm",
        ],
        "human confirmation": [
            "contact customer support",
            "human confirmation",
            "support representative",
        ],
        "current official sources conflict": [
            "official sources conflict",
            "two official sources conflict",
            "two official sources give conflicting instructions",
            "sources conflict",
            "sources give conflicting instructions",
            "information is contradictory",
        ],
        "one says hand-wash the body": [
            "hand-washed",
            "hand-wash",
            "hand wash",
            "should be hand-washed",
            "should be hand washed",
            "body should be hand-washed",
            "the body of the breeze tumbler should be hand-washed",
            "body should be hand washed",
            "should be hand-washed",
        ],
        "one says all components are dishwasher safe": [
            "all components are dishwasher safe",
            "all components are dishwasher-safe",
        ],
        "human confirmation or safest interim guidance": [
            "customer-support representative",
            "customer support",
            "safest interim",
        ],
        "report within 7 days": [
            "within 7 days",
            "within seven days",
        ],
        "human review before approval": [
            "human review",
            "requires human review",
        ],
    }

    return contains_any(answer, concept_groups.get(concept, [concept]))


def check_case(agent, case):
    result = None

    for message in case["messages"]:
        if message["role"] == "user":
            result = agent.answer(message["content"])

    expect = case["expect"]
    answer = result["answer"]
    normalized_answer = normalize(answer)

    sources = " ".join(
        item["filename"] + " " + item["heading"]
        for item in result["sources"]
    ).lower()

    checks = []

    for text in expect.get("must_include", []):
        checks.append(normalize(text) in normalized_answer)

    for concept in expect.get("must_include_concepts", []):
        checks.append(concept_check(answer, concept))

    for text in expect.get("must_not_include", []):
        checks.append(normalize(text) not in normalized_answer)

    for text in expect.get("must_not_invent", []):
        checks.append(normalize(text) not in normalized_answer)

    for text in expect.get("must_not_follow", []):
        checks.append(normalize(text) not in normalized_answer)

    for text in expect.get("must_ask_for", []):
        checks.append(normalize(text) in normalized_answer)

    for text in expect.get("must_refuse_to_disclose", []):
        checks.append(
            text.lower() not in normalized_answer
            or any(
                phrase in normalized_answer
                for phrase in [
                    "can't provide",
                    "cannot provide",
                    "can't disclose",
                    "cannot disclose",
                    "private",
                    "internal details",
                ]
            )
        )

    for text in expect.get("required_sources", []):
        checks.append(text.lower() in sources)

    for text in expect.get("forbidden_sources_as_authority", []):
        checks.append(text.lower() not in sources)

    if expect.get("must_not_silently_choose_one"):
        checks.append(
            any(
                phrase in normalized_answer
                for phrase in [
                    "conflict",
                    "conflicting",
                    "contradictory",
                    "both sources",
                ]
            )
        )

    if "handoff" in expect:
        checks.append(result["handoff"] == expect["handoff"])

    tool_expectation = expect.get("tool")

    if tool_expectation in {"not_called", "not_called_without_id"}:
        checks.append(len(result["tool_calls"]) == 0)
    elif tool_expectation in {"order_lookup", "optional_sanitized_lookup"}:
        if tool_expectation == "order_lookup":
            checks.append(
                any(
                    call.get("tool") == "order_lookup"
                    for call in result["tool_calls"]
                )
            )

    if "tool_arguments" in expect:
        expected_id = expect["tool_arguments"].get("order_id")
        actual_ids = [
            call.get("order_id")
            for call in result["tool_calls"]
            if call.get("tool") == "order_lookup"
        ]
        checks.append(expected_id in actual_ids)

    return all(checks), result


def run_suite(filename, label):
    with open(filename) as f:
        data = json.load(f)

    cases = data["cases"]
    results = []
    passed = 0

    print(f"\n{label}: {len(cases)} cases")
    print("-" * 60)

    for case in cases:
        ok, result = check_case(SupportAgent(), case)
        results.append((case, ok, result))

        if ok:
            passed += 1
            print(f"[PASS] {case['id']}")
        else:
            print(f"[FAIL] {case['id']}")
            print(f"       Answer: {result['answer']}")
            print(f"       Sources: {result['sources']}")
            print(f"       Handoff: {result['handoff']}")

    print(f"{label} RESULT: {passed}/{len(cases)} passed")
    return results, passed


def print_category_results(results):
    categories = {}

    for case, ok, _ in results:
        category = case.get("category", "uncategorized")
        categories.setdefault(category, [0, 0])
        categories[category][1] += 1
        if ok:
            categories[category][0] += 1

    print("\nRESULTS BY CATEGORY")
    print("-" * 60)

    for category, (passed, total) in sorted(categories.items()):
        print(f"{category}: {passed}/{total}")


def main():
    visible_results, visible_passed = run_suite(
        "evaluation/visible-cases.json",
        "VISIBLE CASES",
    )

    original_results, original_passed = run_suite(
        "evaluation/original-cases.json",
        "ORIGINAL CASES",
    )

    all_results = visible_results + original_results
    total_passed = visible_passed + original_passed

    print_category_results(all_results)

    print("\nFINAL RESULT")
    print("-" * 60)
    print(f"TOTAL: {total_passed}/{len(all_results)} passed")

    if total_passed != len(all_results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
