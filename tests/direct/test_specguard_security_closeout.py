import json
from datetime import datetime, timezone

import pytest

from .test_specguard import (
    CONTRACT,
    EVIDENCE_2,
    IMPLEMENTATION,
    SPEC,
    active_contract,
    address,
    chain_now,
    create,
    deploy,
    digest,
    finalize,
    manifest,
    policy,
    submit,
    wire_mocks,
)


def _challenge_manifest(prefix: str, first: bytes, second: bytes) -> str:
    return json.dumps({"sources": [
        {"id": prefix + "1", "authority": prefix.lower() + ".incident.example.net", "artifact_type": "record",
         "url": "https://" + prefix.lower() + ".incident.example.net/counter.txt", "hash": digest(first),
         "criteria": ["C1"], "metadata": "Independent record"},
        {"id": prefix + "2", "authority": prefix.lower() + ".archive.example.edu", "artifact_type": "audit",
         "url": "https://" + prefix.lower() + ".archive.example.edu/counter.txt", "hash": digest(second),
         "criteria": ["C1"], "metadata": "Independent corroboration"},
    ]})


def _cited_manifest(rows) -> str:
    return json.dumps({"sources": [
        {"id": identifier, "authority": authority, "artifact_type": "record", "url": url,
         "hash": digest(body), "criteria": ["C1"], "metadata": "Committed fixture"}
        for identifier, authority, url, body in rows
    ]})


def _policy_with_minimum(minimum: int) -> str:
    return json.dumps({"criteria": [{"id": "C1", "description": "The committed reports support the requirement.",
                                      "critical": True, "min_authorities": minimum,
                                      "satisfaction_rule": "evidence_supports_requirement"}],
                       "challenge_window": 3600})


def _wire_extra_evidence(direct_vm, rows, answer):
    for _, _, url, body in rows:
        direct_vm.mock_web(url.replace("https://", ""), {"status": 200, "body": body})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", json.dumps(answer))


def _advance_to_challenge_deadline(contract, direct_vm, guard_id="SG-001"):
    row = contract.get_guard(guard_id)
    direct_vm._datetime = datetime.fromtimestamp(int(row.challenge_deadline), timezone.utc).isoformat().replace("+00:00", "Z")


def test_invalid_challenge_hash_preserves_approval_and_deposit(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    first, counter, second = _challenge_manifest("BAD", b"counter one", b"counter two"), b"counter one", b"counter two"
    value = json.loads(first)
    value["sources"][0]["hash"] = digest(b"different bytes")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "BAD-001", json.dumps(value), "Malformed counterevidence")
    direct_vm.mock_web(r"bad\.incident\.example\.net/counter\.txt", {"status": 200, "body": counter})
    direct_vm.mock_web(r"bad\.archive\.example\.edu/counter\.txt", {"status": 200, "body": second})
    direct_vm.sender = direct_alice
    contract.review_challenge("SG-001")
    assert contract.get_guard("SG-001").status == "challenged"
    _advance_to_challenge_deadline(contract, direct_vm)
    contract.finalize_preliminary("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "approved" and int(row.deposit) == 10**15


def test_unavailable_challenge_source_cannot_refund_sponsor(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    counter_manifest = _challenge_manifest("DOWN", b"counter one", b"counter two")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "DOWN-001", counter_manifest, "Unavailable source")
    direct_vm.mock_web(r"down\.incident\.example\.net/counter\.txt", {"status": 503, "body": b"outage"})
    direct_vm.mock_web(r"down\.archive\.example\.edu/counter\.txt", {"status": 503, "body": b"outage"})
    direct_vm.sender = direct_alice
    contract.review_challenge("SG-001")
    _advance_to_challenge_deadline(contract, direct_vm)
    contract.expire("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "approved" and int(row.deposit) == 10**15


def test_cross_manifest_evidence_id_collision_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    original = json.loads(manifest())
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert():
        contract.challenge("SG-001", "COLLIDE-001", json.dumps(original), "Replayed evidence IDs")


def test_multiple_distinct_challengers_cannot_be_monopolized(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    m1 = _challenge_manifest("ONE", b"one-a", b"one-b")
    m2 = _challenge_manifest("TWO", b"two-a", b"two-b")
    m3 = _challenge_manifest("THREE", b"three-a", b"three-b")
    direct_vm.sender = direct_bob
    contract.challenge("SG-001", "ONE-001", m1, "First challenge")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "TWO-001", m2, "Second challenge")
    direct_vm.sender = direct_alice
    contract.challenge("SG-001", "THREE-001", m3, "Third challenge")
    with direct_vm.expect_revert():
        direct_vm.sender = direct_bob
        contract.challenge("SG-001", "FOUR-001", m3, "Slot exhaustion")
    assert len(json.loads(contract.get_guard("SG-001").challenge_records)) == 3


def test_reviewed_challenge_does_not_truncate_other_challenge_rights(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    m1 = _challenge_manifest("ONE", b"one-a", b"one-b")
    m2 = _challenge_manifest("TWO", b"two-a", b"two-b")
    direct_vm.sender = direct_bob
    contract.challenge("SG-001", "ONE-001", m1, "First challenge")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "TWO-001", m2, "Second challenge")
    direct_vm.mock_web(r"one\.incident\.example\.net/counter\.txt", {"status": 200, "body": b"one-a"})
    direct_vm.mock_web(r"one\.archive\.example\.edu/counter\.txt", {"status": 200, "body": b"one-b"})
    direct_vm.mock_web(r"two\.incident\.example\.net/counter\.txt", {"status": 200, "body": b"two-a"})
    direct_vm.mock_web(r"two\.archive\.example\.edu/counter\.txt", {"status": 200, "body": b"two-b"})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", '{"bad":"shape"}')
    direct_vm.sender = direct_alice
    contract.review_challenge("SG-001")
    assert contract.get_guard("SG-001").status == "challenged"
    # The second challenge remains reviewable and its slot was not consumed by
    # the first review.
    contract.review_challenge("SG-001")
    assert len(json.loads(contract.get_guard("SG-001").challenge_records)) == 2


def test_authenticated_provenance_policy_is_rejected_until_runtime_support_exists(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    authenticated = json.loads(policy())
    authenticated["provenance_requirement"] = "authenticated"
    with direct_vm.expect_revert():
        create(contract, direct_vm, direct_alice, direct_bob, direct_charlie,
               acceptance_policy=json.dumps(authenticated))


def test_same_origin_cannot_satisfy_independence_with_different_labels(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_bob
    contract.accept_guard("SG-001")
    same_origin = json.loads(manifest())
    same_origin["sources"][0]["authority"] = "first-label.example.com"
    same_origin["sources"][0]["url"] = "https://shared.example.com/one.txt"
    same_origin["sources"][1]["authority"] = "second-label.example.com"
    same_origin["sources"][1]["url"] = "https://shared.example.com/two.txt"
    with direct_vm.expect_revert():
        submit(contract, direct_vm, direct_bob, evidence_manifest=json.dumps(same_origin))
    row = contract.get_guard("SG-001")
    assert row.status == "active" and row.implementation_url == ""
    submit(contract, direct_vm, direct_bob, evidence_manifest=manifest())
    assert contract.get_guard("SG-001").status == "submitted"


def test_cited_evidence_must_have_mutually_independent_authority_origin_pairs(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    rows = [
        ("EV1", "authority-a.example", "https://shared.example.com/one.txt", b"one"),
        ("EV2", "authority-b.example", "https://shared.example.com/two.txt", b"two"),
        ("EV3", "authority-c.example", "https://independent.example.net/three.txt", b"three"),
    ]
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie,
           acceptance_policy=_policy_with_minimum(2))
    direct_vm.sender = direct_bob
    contract.accept_guard("SG-001")
    submit(contract, direct_vm, direct_bob, evidence_manifest=_cited_manifest(rows))
    direct_vm.mock_web(r"spec\.example\.org/contract\.txt", {"status": 200, "body": SPEC})
    direct_vm.mock_web(r"build\.example\.net/result\.txt", {"status": 200, "body": IMPLEMENTATION})
    direct_vm.mock_web(r"shared\.example\.com/one\.txt", {"status": 200, "body": b"one"})
    direct_vm.mock_web(r"shared\.example\.com/two\.txt", {"status": 200, "body": b"two"})
    direct_vm.mock_web(r"independent\.example\.net/three\.txt", {"status": 200, "body": b"three"})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", json.dumps({
        "criteria": [{"id": "C1", "status": "pass", "evidence_ids": ["EV1", "EV2"], "rationale": "Two cited labels share one origin."}],
        "confidence": 99, "rationale": "The cited sources are not independently hosted."}))
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "retryable" and row.reason == "semantic_analysis_insufficient_corroboration"

    # A leader cannot override the same deterministic insufficiency detected by
    # the validator; the guard remains non-authorizing.
    direct_vm._datetime = datetime.fromtimestamp(int(row.next_review_at), timezone.utc).isoformat().replace("+00:00", "Z")
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"spec\.example\.org/contract\.txt", {"status": 200, "body": SPEC})
    direct_vm.mock_web(r"build\.example\.net/result\.txt", {"status": 200, "body": IMPLEMENTATION})
    direct_vm.mock_web(r"shared\.example\.com/one\.txt", {"status": 200, "body": b"one"})
    direct_vm.mock_web(r"shared\.example\.com/two\.txt", {"status": 200, "body": b"two"})
    direct_vm.mock_web(r"independent\.example\.net/three\.txt", {"status": 200, "body": b"three"})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", json.dumps({
        "criteria": [{"id": "C1", "status": "pass", "evidence_ids": ["EV1", "EV3"], "rationale": "The cited sources use two origins."}],
        "confidence": 92, "rationale": "The cited sources are independently hosted."}))
    contract.review("SG-001")
    assert contract.get_guard("SG-001").status == "preliminary_approved"


def test_global_independence_counts_cannot_fake_three_source_matching(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    rows = [
        ("EV1", "authority-a.example", "https://origin-x.example/one.txt", b"one"),
        ("EV2", "authority-b.example", "https://origin-x.example/two.txt", b"two"),
        ("EV3", "authority-c.example", "https://origin-y.example/three.txt", b"three"),
        ("EV4", "authority-c.example", "https://origin-z.example/four.txt", b"four"),
    ]
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie,
           acceptance_policy=_policy_with_minimum(3))
    direct_vm.sender = direct_bob
    contract.accept_guard("SG-001")
    submit(contract, direct_vm, direct_bob, evidence_manifest=_cited_manifest(rows))
    for _, _, url, body in rows:
        direct_vm.mock_web(url.replace("https://", ""), {"status": 200, "body": body})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", json.dumps({
        "criteria": [{"id": "C1", "status": "pass", "evidence_ids": ["EV1", "EV2", "EV3", "EV4"], "rationale": "All globally distinct labels and origins are cited."}],
        "confidence": 98, "rationale": "The global counts appear sufficient."}))
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    assert contract.get_guard("SG-001").status == "retryable"


def test_challenge_provider_retry_can_be_recovered_and_substantiated(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    counter_manifest = _challenge_manifest("RETRY", b"counter one", b"counter two")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "RETRY-001", counter_manifest, "Counterevidence is materially contradictory")
    direct_vm.mock_web(r"retry\.incident\.example\.net/counter\.txt", {"status": 503, "body": b"outage"})
    direct_vm.mock_web(r"retry\.archive\.example\.edu/counter\.txt", {"status": 503, "body": b"outage"})
    direct_vm.sender = direct_alice
    contract.review_challenge("SG-001")
    row = contract.get_guard("SG-001")
    challenge_rows = json.loads(row.challenge_records)
    assert row.status == "challenged" and challenge_rows[0]["status"] == "unresolved"

    direct_vm._datetime = datetime.fromtimestamp(int(challenge_rows[0]["next_review_at"]), timezone.utc).isoformat().replace("+00:00", "Z")
    direct_vm.clear_mocks()
    wire_mocks(direct_vm, {"criteria": [{"id": "C1", "status": "fail", "evidence_ids": ["RETRY1", "RETRY2"], "rationale": "The counterevidence contradicts the requirement."}],
                            "confidence": 94, "rationale": "The committed counterevidence is materially contradictory."})
    direct_vm.mock_web(r"retry\.incident\.example\.net/counter\.txt", {"status": 200, "body": b"counter one"})
    direct_vm.mock_web(r"retry\.archive\.example\.edu/counter\.txt", {"status": 200, "body": b"counter two"})
    direct_vm.mock_llm(r"Independently assess the hash-bound acceptance criteria", json.dumps({
        "criteria": [{"id": "C1", "status": "fail", "evidence_ids": ["RETRY1", "RETRY2"], "rationale": "The counterevidence contradicts the requirement."}],
        "confidence": 94, "rationale": "The committed counterevidence is materially contradictory."}))
    contract.review_challenge("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "challenged" and json.loads(row.challenge_records)[0]["status"] == "substantiated"
    direct_vm._datetime = datetime.fromtimestamp(int(row.challenge_deadline), timezone.utc).isoformat().replace("+00:00", "Z")
    contract.finalize_preliminary("SG-001")
    assert contract.get_guard("SG-001").status == "blocked"
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert():
        contract.refund_blocked("SG-001")
    direct_vm.sender = direct_alice
    contract.refund_blocked("SG-001")
    assert int(contract.get_guard("SG-001").deposit) == 0


def test_original_failure_during_challenge_is_retryable_not_challenge_invalid(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    counter_manifest = _challenge_manifest("ORIG", b"counter one", b"counter two")
    direct_vm.sender = direct_charlie
    contract.challenge("SG-001", "ORIG-001", counter_manifest, "Original evidence became unavailable")
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"spec\.example\.org/contract\.txt", {"status": 200, "body": SPEC})
    direct_vm.mock_web(r"build\.example\.net/result\.txt", {"status": 200, "body": IMPLEMENTATION})
    direct_vm.mock_web(r"evidence\.example\.com/proof\.txt", {"status": 503, "body": b"outage"})
    direct_vm.mock_web(r"audit\.example\.edu/record\.txt", {"status": 200, "body": EVIDENCE_2})
    direct_vm.mock_web(r"orig\.incident\.example\.net/counter\.txt", {"status": 200, "body": b"counter one"})
    direct_vm.mock_web(r"orig\.archive\.example\.edu/counter\.txt", {"status": 200, "body": b"counter two"})
    direct_vm.sender = direct_alice
    contract.review_challenge("SG-001")
    row = contract.get_guard("SG-001")
    challenge_row = json.loads(row.challenge_records)[0]
    assert row.status == "challenged" and row.preliminary_status == "preliminary_approved"
    assert challenge_row["status"] == "unresolved" and "original_evidence" in row.reason


def test_unauthorized_refund_and_expiry_cannot_move_escrow(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, direct_owner):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm, {"criteria": [{"id": "C1", "status": "fail", "evidence_ids": ["EV1"], "rationale": "Requirement failed."}], "confidence": 90, "rationale": "Blocked."})
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    finalize(contract, direct_vm)
    direct_vm.sender = direct_owner
    with direct_vm.expect_revert():
        contract.refund_blocked("SG-001")
    with direct_vm.expect_revert():
        contract.expire("SG-001")
    direct_vm.sender = direct_alice
    contract.refund_blocked("SG-001")
    assert int(contract.get_guard("SG-001").deposit) == 0
