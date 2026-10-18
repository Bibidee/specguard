# SpecGuard design

> The sections below describe historical v0.2.2 behavior where noted. The
> current source is v0.3.0 and its criterion, provenance, challenge, and
> liveness policy is authoritative for a future deployment.

## v0.3 acceptance policy and challenge lifecycle

At `create_guard`, the sponsor commits canonical JSON containing 1–8 immutable
criteria. Each has a stable ID, bounded description, explicit rule
`evidence_supports_requirement`, criticality, and a minimum count of distinct
declared authorities. The beneficiary must submit a manifest binding each
evidence record to criterion IDs, URL, SHA-256, source type, metadata, and its
declared authority. The contract rejects missing coverage before review.

An initial review stores only `preliminary_approved` or
`preliminary_blocked`; neither is payable. During the immutable policy's
challenge window, an affected role may submit one distinct counterevidence
manifest. Validators then reassess the original material plus counterevidence.
That result can reverse the preliminary outcome. A challenged guard cannot pay;
on the bounded deadline it follows the safe refund terminal path. This is an
application-level challenge, not a mutation of GenLayer's native appeal model.

## v0.3 liveness rule

Both review and challenge infrastructure failures receive a 15-minute cooldown
and a matching deadline extension, capped at seven days. This corrects the
v0.2.2 near-deadline cooldown problem while retaining a finite termination path.
Semantic uncertainty never becomes approval, and no provider outage produces a
beneficiary payout.

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
when the primary source is unavailable or fails its hash commitment, and only
bytes matching the original SHA-256 are accepted. A changed sponsor-hosted
response cannot by itself force a blocked result or sponsor refund: an exact
registered mirror may supply the agreed bytes. If neither source verifies, the
outcome is retryable and non-authorizing.

The consumer has a bounded exclusive right to settle an approved guard. After
seven days the beneficiary may settle the already-approved escrow. The sponsor
has no approved-settlement path. `sponsor_counts` measures active funded cases,
not lifetime creations, and is decremented exactly once by the common terminal
settlement path.

## Review deadlines and bounded availability grace

`retryable` never authorizes payment. An infrastructure-classified observation
(fetch, provider, or model-execution unavailability) sets a 15-minute review
cooldown and extends the review deadline by the same amount, capped at a total
of seven days per guard. This gives a bounded retry opportunity without making
escrow indefinite.

A non-dictionary result from the nondeterministic consensus boundary is stored
as `retryable / consensus_unavailable`, also with the 15-minute cooldown, but
does **not** consume the infrastructure-grace budget or extend the deadline.
Consequently, if it happens near the already-agreed review deadline, there may
be no time for another review before normal expiry refunds the sponsor. This is
an explicit finite-liveness trade-off in v0.2.2: it cannot authorize payment,
and neither party can force an approval, but it does not guarantee a retry in
the final 15 minutes. The Direct Mode suite exercises this exact boundary.

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
