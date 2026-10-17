import hashlib
import json
from datetime import datetime, timezone

import pytest


CONTRACT = "contracts/specguard.py"
SPEC_URL = "https://spec.example.org/contract.txt"
IMPLEMENTATION_URL = "https://build.example.net/result.txt"
EVIDENCE_URL = "https://evidence.example.com/proof.txt"
SPEC = b"The report must state: security regression tests passed."
IMPLEMENTATION = b"Release report: security regression tests passed."
EVIDENCE = b"Independent CI record confirms the release report passed security regression tests."


def digest(raw):
    return "0x" + hashlib.sha256(raw).hexdigest()


def address(value):
    return "0x" + value.hex() if isinstance(value, bytes) else value.as_hex


def chain_now(direct_vm):
    return int(datetime.fromisoformat(direct_vm._datetime.replace("Z", "+00:00")).replace(tzinfo=timezone.utc).timestamp())


def deploy(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.check_pickling = True
    return direct_deploy(CONTRACT, sdk_version="v0.2.16")


def create(contract, direct_vm, direct_alice, direct_bob, direct_charlie, **changes):
    direct_vm.sender = direct_alice
    fields = {
        "guard_id": "SG-001", "beneficiary": address(direct_bob), "consumer": address(direct_charlie),
        "brief": "Verify the submitted release report states that security regression tests passed.",
        "spec_url": SPEC_URL, "spec_hash": digest(SPEC),
        "deliver_by": chain_now(direct_vm) + 7200, "review_window": 7200,
    }
    fields.update(changes)
    direct_vm.value = 10**15
    contract.create_guard(**fields)
    direct_vm.value = 0
    return fields


def submit(contract, direct_vm, direct_bob, **changes):
    direct_vm.sender = direct_bob
    fields = {
        "guard_id": "SG-001", "artifact_kind": "text", "implementation_url": IMPLEMENTATION_URL,
        "implementation_hash": digest(IMPLEMENTATION), "evidence_url": EVIDENCE_URL,
        "evidence_hash": digest(EVIDENCE), "summary": "Release report and independent CI evidence are supplied.",
    }
    fields.update(changes)
    contract.submit_implementation(**fields)
    return fields


def wire_mocks(direct_vm, answer=None, implementation=IMPLEMENTATION, evidence=EVIDENCE):
    direct_vm.mock_web(r"spec\.example\.org/contract\.txt", {"status": 200, "body": SPEC})
    direct_vm.mock_web(r"build\.example\.net/result\.txt", {"status": 200, "body": implementation})
    direct_vm.mock_web(r"evidence\.example\.com/proof\.txt", {"status": 200, "body": evidence})
    response = answer or {"spec_match": "yes", "evidence_support": "yes", "risk": "no", "confidence": 92, "rationale": "The report and independent CI evidence satisfy the fixed requirement."}
    direct_vm.mock_llm(r"Independently assess a specification-conformance escrow", json.dumps(response))


def active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_bob
    contract.accept_guard("SG-001")
    submit(contract, direct_vm, direct_bob)
    return contract


def test_create_accept_submit_persists_commitments(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    row = contract.get_guard("SG-001")
    assert row.status == "submitted"
    assert row.sponsor.as_hex.lower() == address(direct_alice).lower()
    assert row.beneficiary.as_hex.lower() == address(direct_bob).lower()
    assert row.consumer.as_hex.lower() == address(direct_charlie).lower()
    assert int(row.deposit) == 10**15
    assert contract.get_info()["version"] == "0.1.1"


@pytest.mark.parametrize("field,value", [
    ("guard_id", "bad id"), ("spec_hash", "0x12"),
    ("spec_url", "http://spec.example.org/x"), ("spec_url", "https://127.0.0.1/x"),
    ("brief", " "),
])
def test_create_rejects_invalid_input(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, field, value):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    with direct_vm.expect_revert():
        create(contract, direct_vm, direct_alice, direct_bob, direct_charlie, **{field: value})


def test_duplicate_and_non_beneficiary_submission_rejected(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    with direct_vm.expect_revert():
        create(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_bob
    contract.accept_guard("SG-001")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert():
        contract.submit_implementation("SG-001", "text", IMPLEMENTATION_URL, digest(IMPLEMENTATION), EVIDENCE_URL, digest(EVIDENCE), "wrong caller")


def test_approved_review_and_designated_consumer_settlement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    assert contract.get_guard("SG-001").status == "approved"
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert():
        contract.settle_approved("SG-001")
    direct_vm.sender = direct_charlie
    contract.settle_approved("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "paid_beneficiary"
    assert int(row.deposit) == 0
    assert int(row.settled_amount) == 10**15


@pytest.mark.parametrize("answer", [
    {"spec_match": "no", "evidence_support": "yes", "risk": "no", "confidence": 92, "rationale": "The implementation misses the mandatory test statement."},
    {"spec_match": "yes", "evidence_support": "yes", "risk": "yes", "confidence": 92, "rationale": "The evidence contains a material contradiction."},
])
def test_semantic_rejection_blocks_and_refunds(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, answer):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm, answer)
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    assert contract.get_guard("SG-001").status == "blocked"
    contract.refund_blocked("SG-001")
    assert contract.get_guard("SG-001").status == "refunded_sponsor"


def test_malformed_output_fails_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm, {"bad": "shape"})
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    row = contract.get_guard("SG-001")
    assert row.status == "retryable"
    assert int(row.deposit) == 10**15


def test_hash_mismatch_never_approves(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = active_contract(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    wire_mocks(direct_vm, implementation=b"changed bytes")
    direct_vm.sender = direct_alice
    contract.review("SG-001")
    assert contract.get_guard("SG-001").status == "blocked"


def test_timeout_and_unaccepted_cancellation_refund(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_alice
    contract.cancel_unaccepted("SG-001")
    assert contract.get_guard("SG-001").status == "cancelled"
    create(contract, direct_vm, direct_alice, direct_bob, direct_charlie, guard_id="SG-002")
    direct_vm._datetime = datetime.fromtimestamp(chain_now(direct_vm) + 7201, timezone.utc).isoformat().replace("+00:00", "Z")
    contract.expire("SG-002")
    assert contract.get_guard("SG-002").status == "refunded_sponsor"
