import json
from datetime import datetime, timezone

import pytest

from .test_specguard import (
    CONTRACT,
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
    same_origin = json.loads(manifest())
    same_origin["sources"][0]["authority"] = "first-label.example.com"
    same_origin["sources"][0]["url"] = "https://shared.example.com/one.txt"
    same_origin["sources"][1]["authority"] = "second-label.example.com"
    same_origin["sources"][1]["url"] = "https://shared.example.com/two.txt"
    with direct_vm.expect_revert():
        create(contract, direct_vm, direct_alice, direct_bob, direct_charlie, evidence_manifest=json.dumps(same_origin))


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
