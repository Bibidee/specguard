# SpecGuard

> **v0.3.0 is the canonical verified StudioNet release.** Its frozen source,
> deployment, byte-for-byte source parity, and live approved settlement are
> recorded below. Earlier deployments remain historical only.

SpecGuard is a standalone GenLayer Intelligent Contract primitive for releasing
an escrowed conformance bond only after a hash-bound implementation satisfies a
precommitted, criterion-level acceptance policy with corroborated evidence. It
is designed for software releases, vendor deliverables, security remediations,
and any workflow where a downstream consumer needs a one-time, consensus-backed
authorization gate.

## What it does

1. A sponsor funds a guard with an immutable JSON policy containing stable
   criterion IDs, descriptions, criticality, corroboration thresholds, and a
   bounded challenge window.
2. The beneficiary accepts, then commits an implementation and evidence manifest
   that binds source IDs, declared authorities, URLs, SHA-256 digests, metadata,
   and applicable criteria.
3. Independent GenLayer validators re-fetch every relevant byte stream, verify
   commitments, enforce provenance coverage, and independently derive a
   criterion-level result.
4. A preliminary result enters a bounded challenge period. One affected party
   may submit committed counterevidence; that review can overturn the result.
5. Only a final approved guard can pay the beneficiary, and only its designated
   consumer has the initial settlement right.

SpecGuard is an escrow primitive, not a deployment platform. It does not prove
real-world identity, make external systems execute a change, authenticate an
HTTPS publisher, or guarantee an LLM judgment is correct.

## Security model

- Exact raw bytes are SHA-256 verified before text decoding or visual review.
- Artifact URLs require HTTPS and reject credentials, fragments, local names,
  and all numeric IP-literal authorities.
- Artifact text and visible image text are quoted as untrusted data; embedded
  instructions are never reviewer instructions.
- Every policy criterion must be `pass`; any `fail` blocks authorization, while
  `unclear`, missing, unavailable, or low-confidence assessment is retryable.
- A passing criterion must cite the policy's minimum number of distinct
  **declared** authorities. A mirror or two URLs declared under one authority
  count once, and declarations do not prove real-world identity.
- Validators agree on criterion statuses, critical failures, provenance state,
  final outcome, and confidence within 20 points—not free-form rationale.
- Every payout uses a single transfer helper and follows debit-in-storage,
  persist-state, then emit-transfer ordering.

## Lifecycle

`funded -> active -> submitted -> preliminary_approved -> approved -> paid_beneficiary`

`submitted -> preliminary_blocked -> blocked -> refunded_sponsor`

`preliminary_* -> challenged -> approved | blocked | retryable`, followed by a
safe sponsor refund if a review or material challenge reaches its bounded
deadline unresolved. A sponsor may cancel only before beneficiary acceptance.

SpecGuard also lets the beneficiary register one HTTPS specification mirror while
the guard is active. It is used whenever the sponsor-controlled primary cannot
verify against the original SHA-256, including a substituted response. Neither
source can authorize a review unless its bytes match that commitment; if both
cannot verify, the guard remains retryable rather than becoming an automatic
sponsor refund.

## Development

Only `contracts/specguard.py` is a deployable contract source. Test modules are
outside `contracts/` so GenVM source discovery cannot accidentally lint pytest
imports as deployable code.

```text
python -m pip install -r requirements.txt
python -m pytest tests -q
python scripts/preflight.py
```

See [the design](docs/DESIGN.md), [security model](docs/SECURITY.md),
[consensus rules](docs/CONSENSUS.md), and [test matrix](docs/TESTING.md).

## What GenLayer adds

Without independent validators, the party running one off-chain model could
selectively accept convenient evidence and release escrow. Here, leader and
validators independently retrieve the committed materials and must agree on the
criterion-level authorization consequence before any application state can
become payable. The contract still does not guarantee that web publishers,
declared authorities, models, or providers are truthful or available.

## StudioNet release evidence — v0.3.0

The canonical contract is
[`0x79E1948E93a28F3B90001a2cB984566a0BF781C7`](https://explorer-studio.genlayer.com/address/0x79E1948E93a28F3B90001a2cB984566a0BF781C7),
deployed from frozen contract-source commit `d68374aa4ea41a4f685e23cdb66f9f978ce279c9` in
[deployment transaction `0x704484a21ea26daa000e9e523caef81f119680cd0b0e7e7599f3c827aa4682e4`](https://explorer-studio.genlayer.com/tx/0x704484a21ea26daa000e9e523caef81f119680cd0b0e7e7599f3c827aa4682e4).
The finalized deployment reached `MAJORITY_AGREE` with GenVM `SUCCESS`.
`gen_getContractCode` retrieved 38,647 deployed bytes; they exactly match the
38,647 local bytes and SHA-256
`4bab5d8642ae98aa8a9196e4890b6a6d5acc9317664103a250ffead773ee6b36`.

Live guard `SG-LIVE-20261018-A` completed `funded -> active -> submitted ->
retryable -> preliminary_approved -> approved -> paid_beneficiary`. The first
review safely persisted `retryable / malformed_model_output`; the single
controlled retry finalized `MAJORITY_AGREE` with GenVM `SUCCESS` and confidence
100. After an unchallenged on-chain challenge period, finalization and settlement
both finalized with `MAJORITY_AGREE` and GenVM `SUCCESS`. The designated consumer
settled 0.001 GEN, and its
[child transfer](https://explorer-studio.genlayer.com/tx/0x4a16cba604761b8d63202be10c219eb262146d3986b450a561024f8e51583f9a)
finalized with `value_credited: true`. The canonical final record has
`deposit: 0` and `settled_amount: 1000000000000000`. Full receipts, immutable
artifact commitments, and superseded deployment history are in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Historical transaction scripts are intentionally disabled because they can
access a locally unlocked signer and submit writes. The remaining
`scripts/verify_source_parity.mjs` utility is read-only: it verifies finalized
deployment status before retrieving and comparing source bytes.

For the distinction between contract-controlled escrow checks, network-level
value-transfer finality, and the approved live-test plan, see
[docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md).
