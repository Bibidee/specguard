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

## Availability and settlement recovery

The sponsor URL is a hash commitment, not an availability guarantee. During
the active state the beneficiary may register one HTTPS mirror. It is consulted
only after the primary source is unavailable, and only bytes matching the
original SHA-256 are accepted. A primary hash mismatch remains an integrity
failure; mirrors cannot mask substituted content.

The consumer has a bounded exclusive right to settle an approved guard. After
seven days the beneficiary may settle the already-approved escrow. The sponsor
has no approved-settlement path. `sponsor_counts` measures active funded cases,
not lifetime creations, and is decremented exactly once by the common terminal
settlement path.

## Intentional limitations

HTTPS syntax validation cannot control DNS rebinding, redirects, or external
host availability. Body limits apply after the documented web-fetch API returns.
Semantic model and validator-provider availability remain external dependencies;
the contract fails closed and retains a timeout refund path rather than treating
them as approval.

SHA-256 proves byte identity, not publisher identity or external-world truth.
The model evaluates untrusted, quoted artifacts; it cannot authenticate their
claims. Native child-transfer credit is confirmed from the network receipt, not
from an atomic contract callback, so dispatched transfers are never retried.
