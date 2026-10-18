# Testing v0.3

Run `python scripts/preflight.py` for syntax, all tests, GenVM lint, and ABI
schema parity. The Direct Mode suite uses official `genlayer-test` deployment,
sender, web, LLM, and validator facilities.

The suite covers policy validation, duplicate IDs, role authorization, deposit
and deadline boundaries, hash verification, primary/mirror behavior, malformed
model output, bounded infrastructure grace, criterion-complete approval,
critical failures, false independence, validator disagreement, challenge
reversal, stale/duplicate challenge handling, cancellation, expiry, active-case
accounting, and debit-before-dispatch settlement ordering.

Mocks prove conditional contract behavior, not StudioNet provider behavior or
native-token credit. Live verification requires separately finalized receipts
and byte-for-byte source parity for the deployed source.
