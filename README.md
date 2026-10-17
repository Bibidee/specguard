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
5. The designated consumer has a seven-day exclusive approved-settlement
   period. If it disappears, only the beneficiary can settle after that period;
   the sponsor can never reclaim an approved guard.

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

v0.2.0 also lets the beneficiary register one HTTPS specification mirror while
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
