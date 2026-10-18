# SpecGuard design

The current source is v0.4.1 and is not deployed. The v0.3.0 deployment
described in the historical evidence remains useful only for provenance.

## v0.4 acceptance policy and challenge lifecycle

At `create_guard`, the sponsor commits canonical JSON containing 1–8 immutable
criteria. Each has a stable ID, bounded description, explicit rule
`evidence_supports_requirement`, criticality, and a minimum count of distinct
declared authorities and distinct committed HTTPS origins. The beneficiary must
submit a manifest binding each evidence record to criterion IDs, URL, SHA-256,
source type, metadata, and its declared authority. The contract rejects
missing coverage before review. The origin count is an assurance boundary, not
publisher authentication: the runtime has no supported cryptographic
attestation verifier, so policies requesting authenticated provenance are
rejected rather than falsely satisfied.

An initial review stores only `preliminary_approved` or
`preliminary_blocked`; neither is payable. During the immutable policy's
challenge window, up to three distinct affected roles may submit separate
counterevidence manifests. IDs are globally unique across the original and
all accepted challenge manifests. Validators reassess the original material
plus one challenge at a time. A reviewed, independently substantiated
contradiction can reverse the preliminary outcome; invalid, rejected,
abandoned, or unresolved challenges cannot. A challenged guard cannot pay
until the bounded window closes and the aggregate outcome is finalized. This
is an application-level challenge, not a mutation of GenLayer's native appeal
model.

## v0.4.1 liveness and observation classification

Both review and challenge infrastructure failures receive a 15-minute cooldown
and a matching deadline extension, capped at seven days. A temporarily
unresolved challenge keeps its immutable record and becomes reviewable again
after that record's cooldown; another eligible challenge can be reviewed while
the first is waiting. At the deadline, unresolved records are finalized without
changing the original preliminary decision. Hash-invalid challenge evidence is
classified as invalid, while failures in the original specification,
implementation, or evidence are classified as original-source failures and
remain retryable during a challenge. Semantic uncertainty never becomes
approval, and no provider outage produces a beneficiary payout.

For a passing criterion, the model's cited evidence IDs must themselves form a
bounded one-to-one matching of the policy's minimum count: each selected
reference must have a distinct declared authority and a distinct normalized
HTTPS origin. Uncited manifest sources and mismatched authority/origin counts
cannot rescue an insufficient citation set.

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
settlement path. `refund_blocked` is sponsor-authorized and only operates after
a genuine blocked terminal state; `expire` cannot refund a challenged guard
without first applying the challenge finalization policy.

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
