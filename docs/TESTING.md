# Testing v0.4.1

Run `python scripts/preflight.py` for syntax, all tests, GenVM lint, and ABI
schema parity. The Direct Mode suite uses official `genlayer-test` deployment,
sender, web, LLM, and validator facilities.

The suite covers policy validation, duplicate IDs, role authorization, deposit
and deadline boundaries, hash verification, primary/mirror behavior, malformed
model output, bounded infrastructure grace, criterion-complete approval,
critical failures, false independence, cited-origin matching, validator disagreement, challenge
reversal, invalid and unavailable challenge evidence, abandoned challenges,
cross-manifest evidence-ID collisions, three-role challenge fairness, early
challenge retry and deadline boundaries, original-versus-challenge failure
classification, unsupported authenticated provenance, cancellation,
expiry, active-case accounting, unauthorized refund/expiry, and
debit-before-dispatch settlement ordering.

The challenge regressions prove that invalid or unavailable counterevidence
cannot create a sponsor refund; a challenge must be reviewed and substantiated
before it can reverse a preliminary result; up to three distinct eligible roles
can submit without one party consuming the only slot; and deadline closure
preserves the original preliminary decision when no substantiated contradiction
exists.

Mocks prove conditional contract behavior, not StudioNet provider behavior or
native-token credit. Live verification requires separately finalized receipts
and byte-for-byte source parity for the deployed source.
