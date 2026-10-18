# Consensus and equivalence (v0.4.0 source)

Each call to `review` or `review_challenge` copies persisted fields into an
in-memory snapshot before `run_nondet_unsafe`. The leader and every validator
then independently fetch committed specification, implementation, and evidence
bytes; verify hashes and source-policy coverage; and ask the model for bounded
criterion results.

Equivalence requires the same result kind. For an analysis it requires the same
final outcome, the same `(criterion_id, status)` mapping, the same critical
failure IDs, verified provenance, and confidence within 20 points. Rationales
and sufficient evidence references are intentionally not compared verbatim.

That distinction is economically material: a leader-only approval could pay the
beneficiary when another validator sees a critical criterion failure or missing
corroboration. Under this policy that disagreement fails equivalence and cannot
create an approving settlement state.

Application challenges are distinct from GenLayer protocol appeals. A challenge
does not alter a finalized protocol transaction; it opens a new, bounded,
counterevidence review. Up to three distinct roles may submit challenges, and
each record is reviewed independently. A challenge is economically inert until
its evidence is hash-verified and the validator result is a substantiated
contradiction of the original preliminary outcome. Invalid, abandoned,
rejected, or unresolved records preserve that original outcome at the deadline.
Evidence IDs are globally unique across the original and challenge manifests,
so a challenge cannot shadow an earlier source in the validator's index.
