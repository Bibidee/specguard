# SpecGuard

SpecGuard is a standalone GenLayer Intelligent Contract primitive for releasing
an escrowed conformance bond when an implementation demonstrably satisfies an
exact, hash-bound specification. It is designed for software releases,
vendor deliverables, security remediations, AI-generated outputs, and any
workflow where a downstream consumer should receive a one-time consensus-backed
approval only after evidence has been verified.

## What it does

1. A sponsor creates and funds a specification escrow with a fixed specification
   URL and SHA-256 digest.
2. The nominated beneficiary accepts, then submits an implementation artifact,
   supporting evidence, and their SHA-256 digests.
3. Independent GenLayer validators fetch the exact committed bytes, verify the
   digests before decoding, and assess conformance.
4. A bounded consensus result becomes `approved`, `blocked`, or `retryable`.
5. An approved escrow can be settled only by the designated consumer; blocked,
   cancelled, and timed-out work has a deterministic sponsor-recovery path.

SpecGuard is an escrow primitive, not a deployment platform. It does not prove
real-world identity, make external systems execute a change, authenticate an
HTTPS publisher, or guarantee an LLM judgment is correct.

## Security model

- Exact raw bytes are SHA-256 verified before text decoding or visual review.
- Artifact URLs require HTTPS and reject credentials, fragments, local names,
  and all numeric IP-literal authorities.
- Artifact text and visible image text are quoted as untrusted data; embedded
  instructions are never reviewer instructions.
- Approval requires `spec_match=yes`, `evidence_support=yes`, `risk=no`, and
  confidence at least 75 from independently equivalent validator observations.
- Validators agree on the deterministic authorization outcome, not free-form
  rationale. Any outcome disagreement fails consensus; varying rationale cannot
  turn a blocked or retryable review into an approval.
- Every payout uses a single transfer helper and follows debit-in-storage,
  persist-state, then emit-transfer ordering.

## Lifecycle

`funded -> active -> submitted -> approved -> paid_beneficiary`

`submitted -> blocked -> refunded_sponsor`

`submitted <-> retryable`, followed by `expire -> refunded_sponsor` if the
review deadline passes. A sponsor may cancel only before beneficiary acceptance.

## Development

Only `contracts/specguard.py` is a deployable contract source. Test modules are
outside `contracts/` so GenVM source discovery cannot accidentally lint pytest
imports as deployable code.

```text
python -m pip install -r requirements.txt
python -m pytest tests -q
python scripts/preflight.py
```

## StudioNet release evidence

The canonical v0.1.1 deployment is
[`0x70968dd0354236e3Eae6eb6eb9Cd3C3C01A4D0f0`](https://explorer-studio.genlayer.com/address/0x70968dd0354236e3Eae6eb6eb9Cd3C3C01A4D0f0).
Its exact source was retrieved through `gen_getContractCode` and matched this
repository byte-for-byte (SHA-256
`7ca2ef1c1d1d166c6672da8b518b3ae8fb71d4932e9cf4532a18ac6ce2df433b`).

One live guard completed the full lifecycle: funded, accepted, submitted,
approved at confidence 92, and paid to the beneficiary. The 0.001 GEN child
transfer finalized with `value_credited: true`; the final guard ledger records
`deposit: 0` and `settled_amount: 1000000000000000`. Full receipts, immutable
artifact commitments, and the historical v0.1.0 incident are in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
