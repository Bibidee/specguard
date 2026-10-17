# SpecGuard design

## Consensus boundary

SpecGuard copies all storage-backed inputs into a plain in-memory snapshot
before it enters nondeterministic execution. The validator callback fetches and
evaluates the same immutable snapshot and never writes storage. It compares
bounded decision semantics rather than free-form rationale.

For approval, both observations must independently satisfy the exact safe tuple
`yes/yes/no` with confidence `>= 75`. For blocked and retryable outcomes,
agreement on the authorization outcome is enough because neither outcome can
transfer funds to the beneficiary. A validator disagreement between `approved`
and any non-approved result fails consensus.

## Escrow accounting

`deposit` is the only custody ledger. Terms are not used as a payout amount.
Every terminal settlement reads `deposit`, rejects zero, sets it to zero, saves
the status and settlement fields, then emits the native GEN transfer. This makes
every exit path one-shot: payout, rejection refund, cancellation refund, and
deadline refund.

## Intentional limitations

HTTPS syntax validation cannot control DNS rebinding, redirects, or external
host availability. Body limits apply after the documented web-fetch API returns.
Semantic model and validator-provider availability remain external dependencies;
the contract fails closed and retains a timeout refund path rather than treating
them as approval.
