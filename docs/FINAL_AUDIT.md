# SpecGuard final audit

## v0.4.1 remediation closeout and deployment

The current source is `v0.4.1` and is deployed on StudioNet at
`0xCbeD8bb09981a42347C87928d1dCd2A75552b8e8`. This closeout addresses the residual challenge/escrow and
corroboration findings: invalid or unreviewed challenges could reach a refund
path, one challenge could monopolize the window, cited evidence could be less
independent than the manifest-wide counts suggested, and original-source
failures could be misclassified during challenge review. It also rejects
cross-manifest evidence-ID collisions and unsupported authenticated-provenance
policies.

The corrected source preserves independent leader/validator observation,
criterion-level equivalence, fail-closed model parsing, one-shot debit-before-
dispatch settlement, and bounded liveness. The deployment itself was finalized
and source-matched; no funded guard or lifecycle transaction is claimed for
this release pass.

Closeout verification: 49 tests passed, GenVM lint passed, ABI/schema
generation passed, and `scripts/preflight.py` passed. Main CI run
[39158223106](https://github.com/Bibidee/specguard/actions/runs/39158223106)
also passed on merged commit `8082a0a28d2f72650054f135a4ea6b5218cf0d1c`.
The deployment transaction
[`0xd4f781f345ddd48c323ca4dc36f6c18ec1e01f3489365d1e4496b015dc4eae2e`](https://explorer-studio.genlayer.com/tx/0xd4f781f345ddd48c323ca4dc36f6c18ec1e01f3489365d1e4496b015dc4eae2e)
finalized with `MAJORITY_AGREE` and GenVM `SUCCESS`. `gen_getContractCode`
returned 52,925 bytes and matched the local source byte-for-byte. The current
contract source SHA-256 is
`b40b6a205b8cc8683481d0e3d8086f6cb6c6f566163ed3ec773eca7dd1c577c2`.
No funded guard or lifecycle transaction was performed in this deployment pass.

### Regression matrix

| Confirmed mechanism | Corrective invariant | Direct Mode proof |
| --- | --- | --- |
| Invalid counterevidence hash reached `blocked` and refund | Integrity-invalid challenges are recorded as `invalid`; the original preliminary decision is restored at close | `test_invalid_challenge_hash_preserves_approval_and_deposit` |
| Unreviewed challenge expired into sponsor refund | `expire` finalizes the challenge window without settling; only an explicit terminal method can move funds | `test_duplicate_and_stale_challenges_are_rejected`, `test_unavailable_challenge_source_cannot_refund_sponsor` |
| One party monopolized the challenge slot | Three bounded slots, one per eligible role, and no early terminal transition | `test_multiple_distinct_challengers_cannot_be_monopolized`, `test_reviewed_challenge_does_not_truncate_other_challenge_rights` |
| Original/challenge evidence ID shadowing | IDs and `(url, hash)` commitments are globally unique per guard | `test_cross_manifest_evidence_id_collision_is_rejected` |
| Caller-declared labels overstated provenance | Both authority labels and committed origins must be distinct; authenticated mode is rejected without a runtime attestation primitive | same-origin, false-independence, and authenticated-provenance tests |
| Uncited evidence satisfied corroboration | Cited references must form a one-to-one authority/origin matching | `test_cited_evidence_must_have_mutually_independent_authority_origin_pairs`, `test_global_independence_counts_cannot_fake_three_source_matching` |
| Challenge outage became terminal | Unresolved challenge records retain immutable evidence and are retryable after cooldown | `test_challenge_provider_retry_can_be_recovered_and_substantiated` |
| Original-source failure looked like challenge invalidity | Scoped observation errors preserve the preliminary decision and keep the challenge retryable | `test_original_failure_during_challenge_is_retryable_not_challenge_invalid` |
| Unauthorized economic transitions | Sponsor-only blocked refund and role-gated expiry/settlement | `test_unauthorized_refund_and_expiry_cannot_move_escrow` |

The v0.3 deployment and earlier releases below are historical evidence only;
the v0.4.1 address above is the current deployment.

# SpecGuard v0.2.2 historical audit

## Historical v0.3.0 superseding audit note

This document's v0.2.2 custody observations remain historical. v0.3.0 added
immutable criterion policies, distinct-authority corroboration thresholds,
criterion-level validator equivalence, application challenges, and bounded
challenge liveness. It was deployed and source-matched as historical evidence;
it is superseded by the deployed v0.4.1 remediation source above.

Audit branch: `codex/specguard-final-audit`.

This document separates proven contract behavior from network-dependent
behavior. It does not authorize another deployment or live transaction.

## Release identity

- Merged release commit: `ecc0b229800b851abe807e9437a672379a2c4432`
- Canonical StudioNet (chain ID 61999) contract:
  `0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa`
- Frozen source SHA-256:
  `54087ad83eb2e639193ae09278eb503b60592b92c23584266d168ebc2d67ed8c`
- Source parity: `gen_getContractCode` returned 24,797 bytes, equal to the
  local source byte-for-byte and by SHA-256.

The recorded live guard `SG-V022-LIVE-1792274655413` completed
`funded -> active -> submitted -> approved -> paid_beneficiary`. Its review
was finalized with `MAJORITY_AGREE`, GenVM `SUCCESS`, and confidence 93. The
settlement's child transfer was separately finalized with `value_credited: true`
for `1000000000000000` wei. Full transaction links are in
[DEPLOYMENT.md](DEPLOYMENT.md).

## Custody findings

`create_guard()` uses the transaction's `gl.message.value`, validates all
arguments, stores the complete guard only after validation, and increments the
sponsor's active-case count in the same contract execution. Direct Mode proves
that invalid inputs, duplicate identifiers, zero addresses, inadequate funding,
and invalid deadlines persist neither a guard nor a case slot.

That is a contract-state guarantee, not a claim about native-token settlement
on a real failed payable transaction. Historical v0.1.0 showed a StudioNet
event-emission failure where value credit and intended contract state diverged.
v0.2.2 removed that unsupported event emission and has a successful live
payable creation, but intentionally sending invalid value to test rollback could
strand GEN. It was not repeated. The available evidence does not prove that
every protocol-level failed payable call refunds its value.

There is no safe generic rescue method: contract storage cannot distinguish an
unallocated protocol balance from funds committed to an active guard. An
unrestricted withdrawal would endanger valid escrow. Operational mitigation is
to prevalidate the exact payable call, use the ABI/schema, simulate where the
client/runtime supports it, and submit only finalized release parameters.

## Native transfer reconciliation

Settlement performs checks-effects-interactions: it reads `deposit`, rejects
zero, records `deposit = 0`, saves the terminal state and amount, releases the
active-case slot, then calls the contract's sole `_send_gen` dispatch point.
Tests cover role restrictions and repeated terminal operations; the source
regression test confirms the debit precedes the only `emit_transfer` call.

GenLayer describes value transfer as an asynchronous message: a parent
finalizes, then the child transfer is created and credited only when the child
activates. A failed child is not automatically returned. Therefore parent
`paid_beneficiary` proves dispatch and one-shot ledger closure, **not** recipient
credit by itself. The required reconciliation procedure is:

1. Read the parent receipt after `FINALIZED`; verify GenVM `SUCCESS`, recipient,
   value, and `triggered_transactions`.
2. For every listed child transaction, wait for `FINALIZED`.
3. Verify the child recipient and value match the terminal guard record and
   require `value_credited: true`.
4. Record both parent and child receipt hashes. Never retry an emitted transfer:
   duplicate dispatch could pay twice.

The recorded v0.2.2 settlement satisfies all four steps. Future settlements
must be reconciled independently. No contract-only recovery can safely make
this asynchronous protocol behavior atomic.

## Consensus timeout policy

Infrastructure-classified observations are non-authorizing, retryable, and
extend `review_deadline` by 15 minutes per event up to a total seven-day grace.
A non-dictionary consensus result is stored as
`retryable / consensus_unavailable` with the same 15-minute cooldown, but no
deadline extension. The Direct Mode fault-injection regression covers a failure
one second before the deadline, the cooldown conflict, expiry at the exact
deadline, zero beneficiary payment, and sponsor refund.

This is a bounded liveness trade-off, not an approval bypass: neither a sponsor
nor a beneficiary can force `approved` from consensus unavailability. A sponsor
can receive the ordinary expiry refund if consensus is unavailable close enough
to the pre-agreed deadline that cooldown outlasts it. For the small testnet
escrow primitive, this is retained as a disclosed policy rather than changing
the frozen deployed source. A v0.2.3 is not recommended without evidence that
an adversary can deliberately induce this external consensus condition.

## Runtime references

- [GenLayer Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [GenLayer value transfers](https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers)
- [GenLayer messages](https://docs.genlayer.com/developers/intelligent-contracts/features/messages)
- [GenLayer Direct Mode testing](https://docs.genlayer.com/api-references/genlayer-test/direct)

## Unexecuted live-test plan

No transaction below has been sent. They require separate approval.

| Purpose | Role / method | Value | Expected result | Safety control |
| --- | --- | ---: | --- | --- |
| Unauthorized acceptance | unrelated wallet / `accept_guard` | 0 | clean revert; guard remains `funded` | nonpayable; read `get_guard` afterward |
| Unauthorized review | unrelated wallet / `review` | 0 | clean revert; no review count change | nonpayable; read afterward |
| Unauthorized settlement | non-consumer / `settle_approved` | 0 | clean revert; approved escrow unchanged | nonpayable; use only a known approved guard |
| Child-transfer reconciliation | consumer / `settle_approved` | 0 | parent dispatch, then child `FINALIZED` and `value_credited: true` | only after an independently approved guard; never retry parent |
| Invalid payable creation | any / `create_guard` | minimum 0.001 GEN | intentionally **not proposed** | could recreate the historical stranded-value risk |

## Final assessment

No confirmed critical or high-severity contract vulnerability was found in the
frozen v0.2.2 source. The open risks are protocol/runtime assumptions: failed
payable-call credit semantics, asynchronous child transfer finality, external
HTTPS/provider availability, and bounded consensus liveness. These are
disclosed limitations, not guarantees hidden by local tests.
