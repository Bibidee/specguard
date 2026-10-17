# SpecGuard v0.2.2 final audit

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
