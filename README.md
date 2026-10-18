# SpecGuard

> **v0.3.0 is a new, undeployed release candidate.** The StudioNet v0.2.2
> address below remains historical evidence for v0.2.2 only; it is not source
> parity evidence for this upgraded contract.

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

## StudioNet release evidence — v0.2.2

The canonical contract is
[`0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa`](https://explorer-studio.genlayer.com/address/0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa),
deployed from source commit `f666b362a368906af151bb93822f3c55879b0f17`.
The deployed source was retrieved through `gen_getContractCode`: local and
deployed source were each 24,797 bytes, with identical SHA-256
`54087ad83eb2e639193ae09278eb503b60592b92c23584266d168ebc2d67ed8c`.

A live guard completed `funded -> active -> submitted -> approved ->
paid_beneficiary`. The review finalized `MAJORITY_AGREE` with GenVM `SUCCESS`,
confidence 93, and the designated consumer settled the 0.001 GEN escrow. Its
child transfer also finalized with `value_credited: true`; the canonical final
record has `deposit: 0` and `settled_amount: 1000000000000000`. Full receipts,
immutable artifact commitments, and superseded deployment history are in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Historical transaction scripts are intentionally disabled because they can
access a locally unlocked signer and submit writes. The remaining
`scripts/verify_source_parity.mjs` utility is read-only: it verifies finalized
deployment status before retrieving and comparing source bytes.

For the distinction between contract-controlled escrow checks, network-level
value-transfer finality, and the approved live-test plan, see
[docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md).
